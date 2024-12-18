import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pydantic import EmailStr

from event_log import EventLogModel, elogger
from loguru import logger
from config import config
from model import InputModel

sender_email = config.email_sender
authorization_code = config.email_auth_code
email_smtp_host = config.email_smtp_host


async def send_email(
        subject: str,
        body: str,
        recipients: EmailStr,
        *,
        input_: InputModel = InputModel(
            user_id=0,
            msg="test"
        )) -> str:
    try:
        # 创建 MIMEMultipart 对象
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipients
        message["Subject"] = subject
        #
        message.attach(MIMEText(body, "plain"))

        # 创建 SMTP_SSL 会话
        await aiosmtplib.send(
            message,
            hostname=email_smtp_host,
            port=465,
            username=sender_email,
            password=authorization_code,
            use_tls=True,
        )

        logger.success(f"Sending email to {recipients} with subject: {subject} and body: {body}")

        elogger.log(EventLogModel(
            user_id=input_.user_id,
            type='func',
            level=EventLogModel.LEVEL.INFO,
            message=f"send_email({subject}, {body}, {recipients}) "
        ))
        return f"Sending email to {recipients} successfully "
    except Exception as e:
        logger.error(f"Send email error: {e}")
        elogger.log(EventLogModel(
            user_id=input_.user_id,
            type='func',
            level=EventLogModel.LEVEL.ERROR,
            message=f"send_email({subject}, {body}, {recipients}) | {e}"
        ))
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
