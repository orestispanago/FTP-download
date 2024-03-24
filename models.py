class RemoteFile:
    def __init__(self, remote_path, mod_time) -> None:
        self.path = remote_path
        self.mod_time = mod_time
        self.local_path = remote_path[1:]


class RemoteFolder:
    def __init__(self, path) -> None:
        self.path = path
        self.name = path.split("/")[-1]
        self.files = []
        self.newer = []
        self.downloaded = []
        self.download_time = None
        self.ftp_list_time = None

    def summary(self):
        return {
            "name": self.name,
            "total": len(self.files),
            "newer": len(self.newer),
            "downloaded": len(self.downloaded),
            "failed": len(self.newer) - len(self.downloaded),
            "download_time": f"{round(self.download_time, 1)} s",
            "ftp_list_time": f"{round(self.ftp_list_time, 1)} s",
            "status": (
                "ERROR" if len(self.newer) != len(self.downloaded) else "OK"
            ),
        }
