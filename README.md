# NITC-major-project

## Downloading the app (Windows 10 only)

Download streamerIPV4.exe or streamerIPV6.exe for streaming from the dist folder in this repository.
Dowload clientListenerIPV4.exe or clientListenerIPV6.exe for listeners from the dist folder in this repository.

NOTE: Some antivirus apps might consider this binary as malware due to some reasons. You can safely ignore the warning. Also allow the app through firewall so that the app can connect to network. Also ensure that the streamer and listener IP versions are same.

## Setting up project environment
### Requirements
Python 3

If you are using Windows, after cloning the repo
```
pip3 install -r pyrequirements.txt
```
or if you are using Anaconda
```
conda create --name majorproject --file condarequirements.txt
conda activate majorproject
```

Assuming your python/anaconda installation went well, that's all you have to do.
