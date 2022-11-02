from ftplib import FTP
import fnmatch


FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/christina/Mobotix/2022"


def list_recursive(ftp, remotedir, file_paths):
    ftp.cwd(remotedir)
    for entry in ftp.mlsd():
        remotepath = remotedir + "/" + entry[0]
        if entry[1]["type"] == "dir":
            list_recursive(ftp, remotepath, file_paths)
        elif entry[1]["type"] == "file":
            file_paths.append(remotepath)


def get_remote_paths(ip=FTP_IP, user=FTP_USER, passwd=FTP_PASS, folder=FTP_DIR):
    all_paths = []
    with FTP(ip, user, passwd) as ftp:
        list_recursive(ftp, folder, all_paths)
    return all_paths


remote_paths = get_remote_paths()

csv_files = fnmatch.filter(remote_paths, "*x90_y90.csv")
img_files = fnmatch.filter(remote_paths, "*x90_y90.*g")

with open("csv_files.txt", "w") as f:
    for line in csv_files:
        f.write(line + "\n")
with open("img_files.txt", "w") as f:
    for line in img_files:
        f.write(line + "\n")
