import datetime
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import format_datetime

EMAIL_USER = ""
EMAIL_PASS = ""
EMAIL_RECIPIENTS = [""]

logger = logging.getLogger(__name__)

dirname = os.path.dirname(__file__)
mail_template = os.path.join(dirname, "mail_template.html")

with open(mail_template, "r", encoding="utf-8") as f:
    BODY = f.read()


def send_mail(html_table="", subject="No subject", body=""):
    """Sends mail to multiple recipients if necessary"""
    toaddr = ", ".join(EMAIL_RECIPIENTS)
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = toaddr
    msg["Subject"] = subject
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    utc_now_fmt = format_datetime(utc_now, usegmt=True)
    header = f"Email generated at: {utc_now_fmt}"
    body = body.replace("\n", "<br>")
    msg.attach(
        MIMEText(
            BODY.format(header=header, html_table=html_table, body=body),
            "html",
        )
    )
    server = smtplib.SMTP_SSL("smtp.upatras.gr", 465)
    # gmail settings:
    # server = smtplib.SMTP("smtp.gmail.com", 587)
    # server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    text = msg.as_string()
    server.sendmail(EMAIL_USER, EMAIL_RECIPIENTS, text)
    server.quit()
    logger.info(f"Mail sent. Subject: {subject}")
