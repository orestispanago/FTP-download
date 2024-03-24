from ftplib import FTP
import logging

FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/dataloggers"

logger = logging.getLogger(__name__)


def download_paths(remote_paths, local_folder):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for remote_path in remote_paths:
            flat_path = remote_path.replace("/", "")
            local_path = f"{local_folder}/{flat_path}"
            with open(local_path, "wb") as f:
                ftp.retrbinary("RETR " + remote_path, f.write)
            logger.debug(f"Downloaded file: {local_path}")


def rename(remote_paths, prefix=""):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for src_path in remote_paths:
            base_name = src_path.split("/")[-1]
            if not base_name.startswith(prefix):
                dest_path = src_path.replace(base_name, f"{prefix}{base_name}")
                ftp.rename(src_path, dest_path)
                logger.info(f"Renamed {src_path} to {dest_path}")
