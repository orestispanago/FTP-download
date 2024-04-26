import os


class RemoteFile:
    def __init__(self, remote_path, mod_time) -> None:
        self.path = remote_path
        self.mod_time = mod_time
        self.local_path = remote_path[1:]

    def set_download_location(self, local_folder=""):
        remote_path_components = self.path.split("/")
        self.local_path = os.path.join(local_folder, *remote_path_components)

    def __repr__(self):
        return str(self.__dict__)


class RemoteFolder:
    def __init__(self, path, ignore_dirs, ignore_files, local_folder=os.getcwd()):
        self.path = path
        self.local_folder = local_folder
        self.ignore_dirs = ignore_dirs
        self.ignore_files = ignore_files
        self.basename = path.split("/")[-1]
        self.remote_files = []
        self.remote_newer = []
        self.downloaded = []
        self.download_time = 0
        self.list_time = 0

    def summary(self):
        return {
            "name": self.basename,
            "total": len(self.remote_files),
            "newer": len(self.remote_newer),
            "downloaded": len(self.downloaded),
            "failed": len(self.remote_newer) - len(self.downloaded),
            "download_time": f"{round(self.download_time, 1)} s",
            "ftp_list_time": f"{round(self.list_time, 1)} s",
            "status": (
                "ERROR" if len(self.remote_newer) != len(self.downloaded) else "OK"
            ),
        }
