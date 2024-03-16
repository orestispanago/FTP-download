import fnmatch
from ftplib import FTP
import datetime
import os


FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/dataloggers/rsi"


def list_recursive(ftp, remotedir, file_entries, ignore_pattern="*.dat"):
    ftp.cwd(remotedir)
    for entry in ftp.mlsd():
        remote_path = remotedir + "/" + entry[0]
        if entry[1]["type"] == "dir":
            print("Found FTP dir:", remote_path)
            list_recursive(ftp, remote_path, file_entries)
        elif entry[1]["type"] == "file":
            if fnmatch.fnmatch(entry[0], ignore_pattern):
                print(f"Ignored FTP entry: {entry[0]}")
                continue
            remote_entry = {"remote_path": remote_path, "entry": entry}
            file_entries.append(remote_entry)


def get_remote_entries(ftp_dir=FTP_DIR):
    remote_entries = []
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        list_recursive(ftp, ftp_dir, remote_entries)
    return remote_entries


def download(remote_paths, local_folder):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for remote_path in remote_paths:
            flat_path = remote_path.replace("/", "")
            local_path = f"{local_folder}/{flat_path}"
            with open(local_path, "wb") as f:
                ftp.retrbinary("RETR " + remote_path, f.write)
            print("Downloaded file:", local_path)


def download_if_remote_newer(remote_entries):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        skipped_counter = 0
        downloaded_counter = 0
        for remote_entry in remote_entries:
            remote_path = remote_entry["remote_path"]
            remote_mod_time_str = remote_entry["entry"][1]["modify"]
            remote_mod_time = modified_str_to_utc(remote_mod_time_str)
            remote_mod_timestamp = remote_mod_time.timestamp()
            local_path = remote_path[1:]
            if os.path.exists(local_path):
                local_mod_time = os.path.getmtime(local_path)
                local_mod_time = datetime.datetime.fromtimestamp(
                    local_mod_time, tz=datetime.timezone.utc
                )
                local_mod_time_tz = local_mod_time.replace(
                    tzinfo=datetime.timezone.utc
                )
                if local_mod_time_tz == remote_mod_time:
                    skipped_counter += 1
                    continue
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                ftp.retrbinary("RETR " + remote_path, f.write)
            print("Downloaded file:", local_path)
            os.utime(local_path, (remote_mod_timestamp, remote_mod_timestamp))
            downloaded_counter += 1
    print(f"Downloaded {downloaded_counter}, skipped {skipped_counter} files")


def rename(remote_paths, prefix=""):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for src_path in remote_paths:
            base_name = src_path.split("/")[-1]
            if not base_name.startswith(prefix):
                dest_path = src_path.replace(base_name, f"{prefix}{base_name}")
                ftp.rename(src_path, dest_path)
                print(f"Renamed {src_path} to {dest_path}")


def modified_str_to_utc(modified_str):
    modified_dt = datetime.datetime.strptime(modified_str, "%Y%m%d%H%M%S")
    modified_utc = modified_dt.replace(tzinfo=datetime.timezone.utc)
    return modified_utc


remote_entries = get_remote_entries()

download_if_remote_newer(remote_entries)


## Glob-like selection and download example
# remote_paths = [entry["remote_path"] for entry in remote_entries]
# csv_files = fnmatch.filter(remote_paths, "*x90_y90.csv")
# img_files = fnmatch.filter(remote_paths, "*x90_y90.*g")

# download(csv_files, "downloads")

# rename(remote_paths, prefix="rsi1min_")
