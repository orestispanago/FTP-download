# FTP-list-select-download

Gets list of remote file paths in FTP directory recursively.

Selects files based on pattern (glob-like).

Downloads list of remote files to local folder (flattened path).

Renames remote files (adding prefix). Renaming requires FTP write permissions.


```python
## Glob-like selection and download example
remote_paths = [entry["remote_path"] for entry in remote_entries]
csv_files = fnmatch.filter(remote_paths, "*x90_y90.csv")
img_files = fnmatch.filter(remote_paths, "*x90_y90.*g")

download(csv_files, "downloads")

rename(remote_paths, prefix="rsi1min_")
```