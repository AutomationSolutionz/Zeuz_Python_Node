import json
import poplib
import smtplib, ssl, email, imaplib
import time
import datetime
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
        wait
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
            value.append({"Sender": msg.from_, "Receiver": msg.to, "Subject": msg.subject, "Date": msg.date, "Text": msg.text, "htmlBody": msg.html})
        return value
