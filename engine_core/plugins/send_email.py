import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

sender_email = "your email"
authorization_code = "your authorization code"


def send_email(subject, body, recipients):
    logger.success(f"Sending email to {recipients} with subject: {subject} and body: {body}")
    # 创建 MIMEMultipart 对象
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipients
    message["Subject"] = subject
    #
    message.attach(MIMEText(body, "plain"))

    # 创建 SMTP_SSL 会话
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login(sender_email, authorization_code)
        text = message.as_string()
        server.sendmail(sender_email, recipients, text)

    return f"Sending email to {recipients} with subject: {subject} and body: {body}"


email_tools = {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email to the specified email with the subject and content",
        "parameters": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string",
                    "description": "Subject of the email",
                },
                "body": {
                    "type": "string",
                    "description": "The content of the email",
                },
                "recipients": {
                    "type": "string",
                    "description": "The recipients' email addresses",
                }
            },
            "required": ["subject", "body", "recipients"],
        },
    }
}
