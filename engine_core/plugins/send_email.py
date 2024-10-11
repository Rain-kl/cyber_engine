import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from config import config

sender_email = config.email_sender
authorization_code = config.email_auth_code
email_smtp_host = config.email_smtp_host


def send_email(subject, body, recipients) -> str:
    try:
        # 创建 MIMEMultipart 对象
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipients
        message["Subject"] = subject
        #
        message.attach(MIMEText(body, "plain"))

        # 创建 SMTP_SSL 会话
        with smtplib.SMTP_SSL(email_smtp_host, 465) as server:
            server.login(sender_email, authorization_code)
            text = message.as_string()
            server.sendmail(sender_email, recipients, text)

        logger.success(f"Sending email to {recipients} with subject: {subject} and body: {body}")
        return f"Sending email to {recipients} with subject: {subject} and body: {body}"
    except Exception as e:
        logger.error(f"Send email error: {e}")
        raise e


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
