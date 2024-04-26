import fnmatch
from ftplib import FTP
import datetime
import time
import os
import logging
import logging.config
import traceback
import pandas as pd
from mailer import send_mail
from models import RemoteFile, RemoteFolder

FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/dataloggers"
DATALOGGER_DIRS = [
    "eko-ms711",
    "eko-ms711-dni",
    "kintrex",
    "koukouli",
    "meteo",
    "microtops",
    "nilu",
    "rsi",
    "solar",
    "thermi-noise",
]
IGNORE_DIRS = "[0-9][0-3]"
IGNORE_FILES = "*.dat"
DOWNLOAD_DIR = "/media/external/FTP-backup"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_remote_mod_timestamp(mod_time_str):
    modified_dt = datetime.datetime.strptime(mod_time_str, "%Y%m%d%H%M%S")
    modified_dt_tz = modified_dt.replace(tzinfo=datetime.timezone.utc)
    return modified_dt_tz.timestamp()


def list_recursive(ftp, ftp_dir, remote_folder):
    ftp.cwd(ftp_dir)
    for entry in ftp.mlsd():
        remote_path = ftp_dir + "/" + entry[0]
        if entry[1]["type"] == "dir":
            if fnmatch.fnmatch(entry[0], remote_folder.ignore_dirs):
                logger.debug(f"Ignored FTP dir: {entry[0]}")
                continue
            list_recursive(ftp, remote_path, remote_folder)
        elif entry[1]["type"] == "file":
            if fnmatch.fnmatch(entry[0], remote_folder.ignore_files):
                logger.debug(f"Ignored FTP file: {entry[0]}")
                continue
            mod_time = get_remote_mod_timestamp(entry[1]["modify"])
            remote_file = RemoteFile(remote_path, mod_time)
            remote_folder.remote_files.append(remote_file)


def list_remote_files(remote_folder):
    start = time.time()
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        list_recursive(ftp, remote_folder.path, remote_folder)
    remote_folder.list_time = time.time() - start
    logger.debug(f"Found {len(remote_folder.remote_files)} entries at FTP")


def select_remote_newer(remote_folder):
    for remote_file in remote_folder.remote_files:
        remote_file.set_download_location(local_folder=remote_folder.local_folder)
        if os.path.exists(remote_file.local_path):
            local_mod_time = os.path.getmtime(remote_file.local_path)
            if local_mod_time < remote_file.mod_time:
                remote_folder.remote_newer.append(remote_file)
        else:
            remote_folder.remote_newer.append(remote_file)


def download(remote_folder):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for remote_file in remote_folder.remote_newer:
            os.makedirs(os.path.dirname(remote_file.local_path), exist_ok=True)
            with open(remote_file.local_path, "wb") as f:
                ftp.retrbinary("RETR " + remote_file.path, f.write)
            logger.debug(f"Downloaded file: {remote_file.local_path}")
            os.utime(
                remote_file.local_path,
                (remote_file.mod_time, remote_file.mod_time),
            )
            remote_folder.downloaded.append(remote_file)
    logger.debug(f"Downloaded {len(remote_folder.downloaded)} files")


def download_newer(remote_folder):
    list_remote_files(remote_folder)
    select_remote_newer(remote_folder)
    start = time.time()
    try:
        download(remote_folder)
    except TimeoutError:
        logger.error(f"TimeoutError")
    remote_folder.download_time = time.time() - start


def ftp_online():
    try:
        with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
            ftp.voidcmd("NOOP")
        return True
    except TimeoutError:
        return False


def main():
    if ftp_online():
        summaries = []
        for datalogger_dir in DATALOGGER_DIRS:
            ftp_dir = f"/dataloggers/{datalogger_dir}"
            remote_folder = RemoteFolder(
                ftp_dir, IGNORE_DIRS, IGNORE_FILES, local_folder=DOWNLOAD_DIR
            )
            download_newer(remote_folder)
            summaries.append(remote_folder.summary())
        df = pd.DataFrame(summaries)
        print(df)
        send_mail(subject="NAS backup report", html_table=df.to_html(index=False))
    else:
        send_mail(subject="NAS offline")
    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
