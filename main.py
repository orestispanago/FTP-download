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
    "meteo",
    "solar",
]

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_remote_mod_timestamp(mod_time_str):
    modified_dt = datetime.datetime.strptime(mod_time_str, "%Y%m%d%H%M%S")
    modified_dt_tz = modified_dt.replace(tzinfo=datetime.timezone.utc)
    return modified_dt_tz.timestamp()


def list_recursive(ftp, remotedir, file_entries, ignore_pattern="*.dat"):
    ftp.cwd(remotedir)
    for entry in ftp.mlsd():
        remote_path = remotedir + "/" + entry[0]
        if entry[1]["type"] == "dir":
            logger.debug(f"Found FTP dir: {remote_path}")
            list_recursive(ftp, remote_path, file_entries)
        elif entry[1]["type"] == "file":
            if fnmatch.fnmatch(entry[0], ignore_pattern):
                logger.debug(f"Ignored FTP entry: {entry[0]}")
                continue
            mod_time = get_remote_mod_timestamp(entry[1]["modify"])
            remote_file = RemoteFile(remote_path, mod_time)
            file_entries.append(remote_file)


def get_remote_files(remote_folder):
    start = time.time()
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        list_recursive(ftp, remote_folder.path, remote_folder.files)
    remote_folder.ftp_list_time = time.time() - start
    logger.debug(f"Found {len(remote_folder.files)} entries at FTP")


def select_remote_newer(remote_folder):
    for entry in remote_folder.files:
        if os.path.exists(entry.local_path):
            local_mod_time = os.path.getmtime(entry.local_path)
            if local_mod_time < entry.mod_time:
                remote_folder.newer.append(entry)
        else:
            remote_folder.newer.append(entry)


def download(remote_folder):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for remote_file in remote_folder.newer:
            os.makedirs(os.path.dirname(remote_file.local_path), exist_ok=True)
            with open(remote_file.local_path, "wb") as f:
                ftp.retrbinary("RETR " + remote_file.path, f.write)
            logger.debug(f"Downloaded file: {remote_file.local_path}")
            os.utime(
                remote_file.local_path,
                (remote_file.mod_time, remote_file.mod_time),
            )
            remote_folder.downloaded.append(remote_file)
    logger.debug(f"Downloaded {len(remote_folder.files)} files")


def download_newer(remote_folder):
    get_remote_files(remote_folder)
    select_remote_newer(remote_folder)
    start = time.time()
    try:
        download(remote_folder)
        remote_folder.download_time = time.time() - start
    except TimeoutError:
        logger.error(f"TimeoutError")
        remote_folder.download_time = time.time() - start


def main():
    summaries = []
    for datalogger_dir in DATALOGGER_DIRS:
        ftp_dir = f"/dataloggers/{datalogger_dir}"
        rf = RemoteFolder(ftp_dir)
        download_newer(rf)
        summaries.append(rf.summary())
    df = pd.DataFrame(summaries)
    print(df)
    send_mail(subject="NAS backup report", html_table=df.to_html(index=False))
    logger.debug(f"{'-' * 15} SUCCESS {'-' * 15}")


if __name__ == "__main__":
    try:
        main()
    except:
        logger.error("uncaught exception: %s", traceback.format_exc())
