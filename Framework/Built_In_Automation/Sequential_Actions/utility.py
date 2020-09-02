import smtplib, ssl, email, imaplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from pprint import pprint
from quopri import decodestring
from datetime import datetime


# using IMAP protocol
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
    pprint(mail)

    imap.close()
    imap.logout()

    sender_mail_from_response = email.utils.parseaddr(mail["sender"])[-1]
    sender_name_from_response = email.utils.parseaddr(mail["sender"])[0]

    subject_matched = False
    mail_matched = False
    name_matched = False

    if subject_to_check == mail["subject"].strip():
        subject_matched = True
    if sender_mail_to_check == sender_mail_from_response:
        mail_matched = True
    if sender_name_to_check == "":
        name_matched = True
    elif sender_name_to_check.lower().strip() == sender_name_from_response.lower():
        name_matched = True

    if name_matched and mail_matched and subject_matched:
        return True
    else:
        return False


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


if __name__ == "__main__":

    smtp_port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "testingemailforsendmail@gmail.com"
    receiver_email = "mahmood.habib.cuet@gmail.com"
    sender_password = "123test234test"
    subject = "multipart email test"

    email_body_html = """\
        <html>
          <body>
            <p>Hi,<br>
               How are you?<br>
               <a href="http://www.realpython.com">Real Python</a>
               has many great tutorials.
            </p>
          </body>
        </html>
        """
    send_email(
        smtp_server,
        smtp_port,
        sender_email,
        sender_password,
        receiver_email,
        subject,
        email_body_html,
    )
    #
    time.sleep(3)
    # check received email
    imap_host = "imap.gmail.com"
    imap_port = 993
    imap_user = "mahmood.habib.cuet@gmail.com"
    imap_pass = "zmxafgpchukkkkjh"
    select_mailbox = "INBOX"
    subject_to_check = "multipart email test"
    sender_to_check = "testingemailforsendmail@gmail.com"

    result = check_latest_received_email(
        imap_host,
        imap_port,
        imap_user,
        imap_pass,
        select_mailbox,
        subject_to_check,
        sender_to_check,
    )

    if result:
        print("Test Successful")

    else:
        print("Test unsuccessful")
