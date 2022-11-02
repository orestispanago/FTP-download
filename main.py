from ftplib import FTP
import fnmatch


FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/christina/Mobotix/2022/11/02"


def list_recursive(ftp, remotedir, file_paths):
    ftp.cwd(remotedir)
    for entry in ftp.mlsd():
        remotepath = remotedir + "/" + entry[0]
        if entry[1]["type"] == "dir":
            print("Found FTP dir:", remotepath)
            list_recursive(ftp, remotepath, file_paths)
        elif entry[1]["type"] == "file":
            file_paths.append(remotepath)


def get_remote_paths():
    all_paths = []
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        list_recursive(ftp, FTP_DIR, all_paths)
    return all_paths


def download(remote_files, local_folder):
    with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
        for remote_path in remote_files:
            flat_path = remote_path.replace("/", "")
            local_path = f"{local_folder}/{flat_path}"
            with open(local_path, 'wb' ) as f :
                ftp.retrbinary('RETR ' + remote_path, f.write)
            print("Downloaded file:", local_path)


remote_paths = get_remote_paths()

csv_files = fnmatch.filter(remote_paths, "*x90_y90.csv")
img_files = fnmatch.filter(remote_paths, "*x90_y90.*g")

download(csv_files, "downloads")