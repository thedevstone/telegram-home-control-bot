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
5. Create a certificate with openssl. See [**WebHook guide](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)
4. Run yiHomeControlBot.py
```shell
  (venv) python yiHomeControlBot.py
```
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
