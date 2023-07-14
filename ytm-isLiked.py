#!/usr/bin/python

from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
import os
import re
import random
import string
import sys

def getid(source):
    idpatterns = [
        re.compile('/watch\?v=([0-9A-Za-z_-]{11})(?:&|$)'),
        re.compile('^([0-9A-Za-z_-]{11})$')
    ]
    for pattern in idpatterns:
        match = pattern.search(source)
        if match:
            return match.group(1)
    print(f'Error: unable to get ID from "{source}"!')
    sys.exit(1)

if (len(sys.argv) != 2):
    print("Error: incorrect usage!")
    sys.exit(1)

ytid = getid(sys.argv[1])


ytmusic = YTMusic("/home/ashish/.config/ytmusic-oauth.json")


song = ytmusic.get_watch_playlist(ytid, limit=1)["tracks"][0]
if song["videoId"] != ytid:
    print("Error: something is wrong, ytid's don't match!")
    sys.exit(1)

if song["likeStatus"] != "LIKE":
    print('1')
    sys.exit(0)
else:
    print('0')
    sys.exit(1)
