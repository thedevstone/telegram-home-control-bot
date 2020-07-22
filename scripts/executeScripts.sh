#!/bin/bash
nohup sudo python src/yiHomeControlBot.py  > /dev/null 2>&1 &
nohup ./deleteAllMp4.sh &