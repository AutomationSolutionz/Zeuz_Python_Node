import json
import poplib
import random
import re
import secrets
import smtplib, ssl, email, imaplib
import string
import time
import datetime

import os
import requests
from imap_tools import MailBox, AND
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from pprint import pprint
from datetime import datetime
from quopri import decodestring
from email.header import decode_header
from Framework.Utilities import CommonUtil
import inspect
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from html import unescape as html_unescape

# using IMAP protocol
from Framework.Utilities.CommonUtil import MODULE_NAME


def check_latest_received_email(
    imap_host,
    imap_port,
    imap_user,
    imap_pass,
    select_mailbox,
    subject_to_check,
    sender_mail_to_check,
    sender_name_to_check
):
    # Gmail requires to generate One-Time App Password
    # https://security.google.com/settings/security/apppasswords
    IMAP4_HOST = imap_host
    IMAP4_PORT = imap_port
    IMAP4_USER = imap_user
    IMAP4_PASS = imap_pass
    IMAP4_MAILBOX = select_mailbox

    imap = imaplib.IMAP4_SSL(host=IMAP4_HOST, port=IMAP4_PORT)

    imap.login(user=IMAP4_USER, password=IMAP4_PASS)

    imap.select(mailbox=IMAP4_MAILBOX, readonly=False)

    # def get_str(text):
    #     return decodestring(text).decode()
    #
    # def get_date(text):
    #     try:
    #         return datetime.strptime(headers['Date'], '%a, %d %b %Y %H:%M:%S %z')
    #     except ValueError:
    #         return text

    # def get_body(msg):
    #     type = msg.get_content_maintype()
    #
    #     if type == 'multipart':
    #         for part in msg.get_payload():
    #             if part.get_content_maintype() == 'text':
    #                 return part.get_payload()
    #
    #     elif type == 'text':
    #         return msg.get_payload()

    status, result = imap.search(None, "ALL")

    print(status)
    # print(result)
    # status: OK
    # result: [b'1 2 3 4 ...']
    messages = result[0].split()
    latest_email_id = messages[-1]

    status, data = imap.fetch(latest_email_id, "(RFC822)")
    msg = email.message_from_bytes(data[0][1])
    # mail = data[0][1].decode()
    # mail = email.message_from_string(mail)
    #
    # headers = dict(msg._headers)
    # print(headers)
    # mail = {
    #     'to': get_str(headers['To']),
    #     'sender': get_str(headers['From']),
    #     'subject': get_str(headers['Subject']),
    #     'date': get_date(headers['Date']),
    #     # 'body': get_body(mail)
    # }
    mail = {
        "to": msg["To"],
        "sender": msg["From"],
        "subject": msg["Subject"],
        "date": msg["Date"],
        # 'body': get_body(msg)
    }

    imap.close()
    imap.logout()

    sender_mail_from_response = email.utils.parseaddr(mail["sender"])[-1]
    sender_name_from_response = email.utils.parseaddr(mail["sender"])[0]

    msg = "Sender name: %s\nSubject: %s\nSender email: %s" % (sender_name_from_response, mail["subject"], sender_mail_from_response)
    CommonUtil.ExecLog("", msg, 5)

    result = False
    if subject_to_check and subject_to_check == mail["subject"].strip():
        result = True
    elif subject_to_check:
        return False
    if sender_mail_to_check and sender_mail_to_check == sender_mail_from_response:
        result = True
    elif sender_mail_to_check:
        return False
    if sender_name_to_check and sender_name_to_check.lower().strip() == sender_name_from_response.lower():
        result = True
    elif sender_name_to_check:
        return False
    return result


def send_email(
    smtp_server,
    smtp_port,
    sender_email,
    sender_password,
    receiver_email,
    subject,
    body_html,
):
    smtp_server = smtp_server
    port = smtp_port  # For starttls
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Create the plain-text and HTML version of your message
    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(body_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)

    # Attach files to email
    # filename = "Framework/Built_In_Automation/Web/REST/document.txt"  # In same directory as script
    #
    # # Open PDF file in binary mode
    # with open(filename, "rb") as attachment:
    #     # Add file as application/octet-stream
    #     # Email client can usually download this automatically as attachment
    #     part2 = MIMEBase("application", "octet-stream")
    #     part2.set_payload(attachment.read())
    #
    # # Encode file in ASCII characters to send by email
    # encoders.encode_base64(part2)
    #
    # # Add header as key/value pair to attachment part
    # part2.add_header(
    #     "Content-Disposition",
    #     f"attachment; filename= {filename}",
    # )
    #
    # # Add attachment to message and convert message to string
    # message.attach(part2)

    text = message.as_string()

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, text)
        print("email sent successfully")

def delete_mail(
        imap_host,
        imap_user,
        select_mailbox,
        imap_pass,
        subject_to_check,
        text,
        sender_email,
        receiver_email,
        flagged_email,
        check_email,
        exact_date,
        after_date,
        before_date,
        wait=10.0
):
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    # time.sleep(5)

    with MailBox(imap_host).login(imap_user, imap_pass, initial_folder=select_mailbox) as mailboxi:

        clauses = []

        def gt(dt):
            dt = datetime.strptime(dt, '%Y-%m-%d')
            return dt

        if subject_to_check:
            clauses.append(AND(subject=subject_to_check))
        if text:
            clauses.append(AND(text=text))
        if sender_email:
            clauses.append(AND(from_=sender_email))
        if check_email:
            if check_email in ("false", "unseen", "unread", "unchecked", "no"):
                clauses.append(AND(seen=False))
            else:
                clauses.append(AND(seen=True))
        if flagged_email:
            if flagged_email in ("true", "ok", "yes", "flag", "flagged"):
                clauses.append(AND(flagged=True))
            else:
                clauses.append(AND(flagged=False))
        if receiver_email:
            clauses.append(AND(to=receiver_email))
        if exact_date:
            f = gt(exact_date)
            clauses.append(AND(date=datetime.date(f)))
        if after_date:
            a = gt(after_date)
            clauses.append(AND(date_gte=datetime.date(a)))
        if before_date:
            b = gt(before_date)
            clauses.append(AND(date_lt=datetime.date(b)))

        end = time.time() + wait
        while True:
            all_mails = list(mailboxi.fetch(AND(*clauses)))
            if len(all_mails) > 0 or time.time() > end:
                break

        mail_list = []
        for mail in all_mails:
            mail_list.append({
                "uid": mail.uid,
                "from": mail.from_,
                "subject": mail.subject,
                "to": mail.to,
                "text": mail.text,
                "html": mail.html,
            })

        try: log_msg = json.dumps(mail_list, indent=2)
        except: log_msg = str(mail_list)
        CommonUtil.ExecLog(sModuleInfo, "Deleting the following mails:" + log_msg, 1)
        mailboxi.delete([mail["uid"] for mail in mail_list])


def save_mail(
        imap_host,
        imap_user,
        select_mailbox,
        imap_pass,
        subject_to_check,
        text,
        sender_email,
        receiver_email,
        flagged_email,
        check_email,
        exact_date,
        after_date,
        before_date,
        attachment_path,
        wait,
):
    # time.sleep(5)
    with MailBox(imap_host).login(imap_user, imap_pass, initial_folder=select_mailbox) as mailboxi:

        clauses = []

        def gt(dt):
            dt = datetime.strptime(dt, '%Y-%m-%d')
            return dt

        if subject_to_check:
            clauses.append(AND(subject=subject_to_check))
        if text:
            clauses.append(AND(text=text))
        if sender_email:
            clauses.append(AND(from_=sender_email))
        if check_email:
            if check_email in ("false", "unseen", "unread", "unchecked", "no"):
                clauses.append(AND(seen=False))
            else:
                clauses.append(AND(seen=True))
        if flagged_email:
            if flagged_email in ("true", "ok", "yes", "flag", "flagged"):
                clauses.append(AND(flagged=True))
            else:
                clauses.append(AND(flagged=False))
        if receiver_email:
            clauses.append(AND(to=receiver_email))
        if exact_date:
            f = gt(exact_date)
            clauses.append(AND(date=datetime.date(f)))
        if after_date:
            a = gt(after_date)
            clauses.append(AND(date_gte=datetime.date(a)))
        if before_date:
            b = gt(before_date)
            clauses.append(AND(date_lt=datetime.date(b)))

        end = time.time() + wait
        while True:
            all_mails = list(mailboxi.fetch(AND(*clauses)))
            if len(all_mails) > 0 or time.time() > end:
                break

        value = []
        for msg in all_mails:
            value.append({"Sender": msg.from_, "Receiver": msg.to, "Subject": msg.subject, "Date": msg.date, "Text": msg.text, "htmlBody": msg.html, "attachment": msg.attachments})

        if not attachment_path:
            attachment_path = sr.Get_Shared_Variables("zeuz_download_folder") + os.sep + "email_attachments"
        if not os.path.isdir(attachment_path):
            os.makedirs(attachment_path)

        # Todo: If read mail is run multiple times then multiple directory with 0,1,2 in folder_name is needed
        # Todo: If read mail fetches multiple mails then multiple directory with 0,1,2 in folder_name is needed
        # Todo: If user want to rename they should put file_path with commas in action data_set and we need to implement ot here

        for msg in all_mails:
            for att in msg.attachments:
                with open(attachment_path + os.sep + att.filename, 'wb') as f:
                    f.write(att.payload)

        return value

RANDOM_MAIL_TIMEOUT = 30  # seconds per request to the temporary email services


def is_temporary_mail_error(e):
    """True for a requests error worth retrying: rate limit (429), server error or network problem. False for a bad token or deleted mailbox"""
    response = getattr(e, "response", None)
    return response is None or response.status_code == 429 or response.status_code >= 500


class RandomMailBoxExporter(ABC):
    """
    A temporary email service. Credentials are a dict of plain strings {"email": ..., "api_key": ...}
    because test cases store them in a variable and later pass them back as a string that is eval()'d.
    Mails are returned as {email: [{"id", "sender", "subject", "date", "body", "content"}, ...]}
    where body is the html (or text if there is no html) and content is the plain text.
    """

    connection_creds = None

    @abstractmethod
    def get_random_mailbox(self):
        """Create MailBox on the service. Returns credentials in form of dict"""

    @abstractmethod
    def checkMails(self, creds):
        """Returns a dict of the email address to its list of messages"""

    @abstractmethod
    def deleteMailBox(self, creds):
        """Delete mailbox. Returns True or False"""


def _random_mail_username():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))


_HTML_BLOCK_TAGS = [
    "br", "p", "div", "pre", "table", "tr", "td", "th", "ul", "ol", "li", "hr", "blockquote",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "footer", "section", "article",
]


def _html_to_text(html):
    # Only block tags break the line, so "code is <b>123456</b>" stays "code is 123456"
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(_HTML_BLOCK_TAGS):
        tag.insert_after("\n")
    text = "\n".join(line.strip() for line in soup.get_text().splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class TempEmailMailTm(RandomMailBoxExporter):
    """https://docs.mail.tm - api_key holds the account's bearer token"""

    API = "https://api.mail.tm"

    def _request(self, method, path, creds=None, **kwargs):
        # No Accept header: the default JSON-LD response wraps collections in "hydra:member"
        headers = {"Authorization": f"Bearer {creds['api_key']}"} if creds else {}
        response = requests.request(method, self.API + path, headers=headers, timeout=RANDOM_MAIL_TIMEOUT, **kwargs)
        response.raise_for_status()
        return response

    def get_random_mailbox(self):
        domains = [
            d["domain"] for d in self._request("GET", "/domains").json()["hydra:member"]
            if d.get("isActive") and not d.get("isPrivate")
        ]
        if not domains:
            raise Exception("mail.tm has no active public domain")
        account = {"address": f"{_random_mail_username()}@{random.choice(domains)}", "password": secrets.token_urlsafe(16)}
        self._request("POST", "/accounts", json=account)
        token = self._request("POST", "/token", json=account).json()["token"]
        return {"email": account["address"], "api_key": token}

    def checkMails(self, creds):
        var_mails = []
        for summary in self._request("GET", "/messages", creds).json()["hydra:member"]:
            msg = self._request("GET", f"/messages/{summary['id']}", creds).json()
            html = "".join(msg.get("html") or [])
            text = msg.get("text") or ""
            var_mails.append({
                'id': msg["id"],
                'sender': msg["from"]["address"],
                'subject': msg.get("subject") or "",
                'date': msg.get("createdAt") or "",
                'body': html or text,
                'content': text or _html_to_text(html),
            })
        return {creds['email']: var_mails}

    def deleteMailBox(self, creds):
        account_id = self._request("GET", "/me", creds).json()["id"]
        return self._request("DELETE", f"/accounts/{account_id}", creds).status_code == 204


class TempEmailGuerrillaMail(RandomMailBoxExporter):
    """https://www.guerrillamail.com/GuerrillaMailAPI.html - api_key holds the session's sid_token"""

    API = "https://api.guerrillamail.com/ajax.php"
    WELCOME_SENDER = "no-reply@guerrillamail.com"  # every new inbox starts with a welcome mail from here

    def _call(self, params):
        response = requests.get(self.API, params=params, timeout=RANDOM_MAIL_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_random_mailbox(self):
        result = self._call({"f": "get_email_address"})
        return {"email": result["email_addr"], "api_key": result["sid_token"]}

    def checkMails(self, creds):
        var_mails = []
        for summary in self._call({"f": "get_email_list", "offset": 0, "sid_token": creds['api_key']}).get("list", []):
            if summary.get("mail_from") == self.WELCOME_SENDER:
                continue
            msg = self._call({"f": "fetch_email", "email_id": summary["mail_id"], "sid_token": creds['api_key']})
            body = msg.get("mail_body") or ""
            timestamp = int(msg.get("mail_timestamp") or 0)
            var_mails.append({
                'id': str(msg["mail_id"]),
                # Guerrilla Mail html-escapes these, e.g. "ü" comes as "&uuml;"
                'sender': html_unescape(msg.get("mail_from") or ""),
                'subject': html_unescape(msg.get("mail_subject") or ""),
                'date': time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(timestamp)) if timestamp else "",
                'body': body,
                'content': _html_to_text(body),
            })
        return {creds['email']: var_mails}

    def deleteMailBox(self, creds):
        return self._call({"f": "forget_me", "email_addr": creds['email'], "sid_token": creds['api_key']}) is True


def random_mail_factory():
    """Returns the first service that could create a mailbox, with connection_creds set. None if every service failed"""
    sModuleInfo = inspect.currentframe().f_code.co_name + " : " + MODULE_NAME

    for factory in (TempEmailMailTm(), TempEmailGuerrillaMail()):
        try:
            factory.connection_creds = factory.get_random_mailbox()
            return factory
        except Exception as e:
            CommonUtil.ExecLog(sModuleInfo, "%s could not create a mailbox: %s" % (type(factory).__name__, e), 2)
    return None
