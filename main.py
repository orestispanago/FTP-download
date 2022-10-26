from ftplib import FTP

FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/christina/Mobotix/2022"

all_paths = []
csv_files = []
img_files = []

def list_recursive(ftp, remotedir):
    ftp.cwd(remotedir)
    for entry in ftp.mlsd():
        remotepath = remotedir + "/" + entry[0]
        if entry[1]['type'] == 'dir':
            list_recursive(ftp, remotepath)
        elif entry[1]['type'] == 'file':
            all_paths.append(remotepath)
            

with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
    list_recursive(ftp, FTP_DIR)

for f in all_paths:
    if "x90_y90.csv" in f:
        csv_files.append(f)
    elif "x90_y90.jpg"in f or "x90_y90.png" in f:
        img_files.append(f)

with open('csv_files.txt', 'w') as f:
    for line in csv_files:
        f.write(line + "\n")
with open('img_files.txt', 'w') as f:
    for line in img_files:
        f.write(line + "\n")
