# FTP-download

Incremental download fron FTP server.

## Raspberry-Pi setup

To auto-mount an external HDD on the Pi:

1. Use ```blkid``` to get the HDD's UUID:

2. Add the following line to ```/etc/fstab```:

```
UUID=YourUUID /media/external auto nosuid,nodev,nofail,rw,user,exec,umask=000 0 0
```

3. To run every day at 09:01 UTC use:

```
1 9 * * * python3 ~/FTP-alerts/main.py
```