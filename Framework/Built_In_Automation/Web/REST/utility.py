import smtplib, ssl, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase


sender_email = "testingemailforsendmail@gmail.com"
receiver_email = "mahmood.habib.cuet@gmail.com"
sender_password = '123test234test'
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


def send_email(sender_email, sender_password , receiver_email, subject, body_html):
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    message = MIMEMultipart("alternative")
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
    send_email(sender_email, sender_password, receiver_email,subject,email_body_html)