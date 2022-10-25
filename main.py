from ftplib import FTP

FTP_IP = ""
FTP_USER = ""
FTP_PASS = ""
FTP_DIR = "/christina/Mobotix/2022"


csv_files = []
img_files = []

with FTP(FTP_IP, FTP_USER, FTP_PASS) as ftp:
    ftp.cwd(FTP_DIR)
    months = ftp.nlst()[2:]
    for month in months:
        ftp.cwd(f"{FTP_DIR}/{month}")
        days = ftp.nlst()[2:]
        for day in days:
            ftp.cwd(f"{FTP_DIR}/{month}/{day}")
            hours = ftp.nlst()[2:]
            for hour in hours:
                ftp.cwd(f"{FTP_DIR}/{month}/{day}/{hour}")
                minutes = ftp.nlst()[2:]
                for minute in minutes:
                    minute_path = f"{FTP_DIR}/{month}/{day}/{hour}/{minute}"
                    ftp.cwd(minute_path)
                    files = ftp.nlst()[2:]
                    if "x90_y90.csv" in files:
                       csv_files.append(f"{minute_path}/x90_y90.csv")
                    if "x90_y90.jpg" in files:
                        img_files.append(f"{minute_path}/x90_y90.jpg")
                    if "x90_y90.png" in files:
                        img_files.append(f"{minute_path}/x90_y90.png")

                
# common = list(set(csv_files).intersection(jpg_files))
# uncommon = list(set(csv_files).symmetric_difference(jpg_files))

with open('csv_files.txt', 'w') as f:
    for line in csv_files:
        f.write(f"{line}\n")
with open('img_files.txt', 'w') as f:
    for line in img_files:
        f.write(f"{line}\n")