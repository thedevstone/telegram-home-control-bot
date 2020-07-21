# YI Hack Telegram Bot - Face Detection notifications

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Features](#features)
- [Performance](#performance)
- [Supported cameras](#supported-cameras)
- [Donation](#donation)

## Prerequisites
Mp4 videos pushed in directories through **ftp/sftp/ftps/scp** protocols.

### YI Cameras
- Install **YI-Hack** firmware to your camera. [YI-Hack-Allwinner](https://github.com/roleoroleo/yi-hack-Allwinner/ is used in this project
- Enable **ftp push**
- Set up a **ftp server** on a machine (raspberry pi)


## Installation
### Bot Creation
1. Create a Telegram Bot with **BotFather**
2. Write down **Token**
3. Add commands (I have only this command at the moment)
```
  /face_number #Set the number of detected face to send
```
### Python Bot
1. Install python 
2. Install python modules 
```shell
  pip3 install -r requirements.txt
```
3. Create a **config.yaml**. See configExample.yaml
4. Open port **88** on router. Used for Telegram WebHook
5. Create a certificate with openssl. See [**WebHook guide**](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)
6. Run yiHomeControlBot.py
```shell
  (venv) python yiHomeControlBot.py
```
## Raspberry Installation
Make everything works on Raspberry is very tediuous. I have figure out how to do that 
1. **Opencv** is notoriously bastard on raspberry
2. Install these dependecies [thanks to [stackoverflow](https://stackoverflow.com/questions/59080094/raspberry-pi-and-opencv-cant-install-libhdf5-100)]
  ```shell
    sudo apt-get update && sudo apt-get upgrade
    sudo apt-get install build-essential cmake pkg-config
    sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev
    sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
    sudo apt-get install libxvidcore-dev libx264-dev
    sudo apt-get install libfontconfig1-dev libcairo2-dev
    sudo apt-get install libgdk-pixbuf2.0-dev libpango1.0-dev
    sudo apt-get install libgtk2.0-dev libgtk-3-dev
    sudo apt-get install libatlas-base-dev gfortran
    sudo apt-get install libhdf5-dev libhdf5-serial-dev libhdf5-103
    sudo apt-get install libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
    sudo apt-get install python3-dev
  ```
  and these from [piwheels](https://www.piwheels.org/project/opencv-contrib-python/) (can overlap):
  ```shell
    sudo apt install libgtk-3-0 libavformat58 libtiff5 libcairo2 libqt4-test libpango-1.0-0 libopenexr23 libavcodec58 libilmbase23 libatk1.0-0 libpangocairo-1.0-0 libwebp6 libqtgui4 libavutil56 libjasper1 libqtcore4 libcairo-gobject2 libswscale5 libgdk-pixbuf2.0-0
  ```
3. Then install depencies:
  ```shell
    pip3 install -r requirements.txt
  ```
3. Create a **config.yaml**. See configExample.yaml
4. Open port **88** on router. Used for Telegram WebHook
5. Create a certificate with openssl. See [**WebHook guide**](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)
6. Run yiHomeControlBot.py with sudo. Port 88 need sudo. Or choose port 8443 without sudo
  ```shell
    (venv) sudo python yiHomeControlBot.py
  ```
7. Enjoy!

## Features
1. User Authentication
2. Administrator logs
3. **Realtime Face Detection** as soon as a new video is pushed to a **watch folder**
4. Select number of faces to be sent
5. User ban with many attempts

## Performance
Good performance if video present faces. If video does not have faces it has to be analysed entirely

## Supported-Cameras
All cameras supported by **Yi-Hack** projects

## Donation
[**Donation**](paypal.me/LucaGiulianini)
