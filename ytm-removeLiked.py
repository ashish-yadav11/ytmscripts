#!/usr/bin/python

from ytmusicapi import YTMusic
import os
import re
import random
import string
import sys

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"
lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
lkmusicdir = "/media/storage/Music"


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


ytmusic = YTMusic(oauthfile)

lkplylst = ytmusic.get_playlist(lkplylstid, limit=9999)["tracks"]
for song in lkplylst:
    if song["videoId"] == ytid:
        print(f"Notice: removing [{ytid}] from 'Liked Songs'...")
        ytmusic.remove_playlist_items(lkplylstid, [song])
        break
