import os

from dotenv import load_dotenv

dirname = os.path.dirname(__file__)
load_dotenv(os.path.join(dirname, ".env"))

FTP_IP = os.getenv("FTP_IP")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
