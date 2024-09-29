#!/usr/bin/python

from ytmusicapi import YTMusic
import os
import re
import sys

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"
unplylstid = "PL9cE5Kd6uzpiu0WpDfY5T4rexKsYoa4E7"
unmusicdir = "/media/storage/Music/archive"


def handleexception(funcname, e):
    print(f'Error: {funcname}() failed with the following error!')
    print(e)

def call(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        handleexception(f.__name__, e)
        sys.exit(1)


def getid(source):
    idpatterns = [
        re.compile('/watch\\?v=([0-9A-Za-z_-]{11})(?:&|$)'),
        re.compile('^([0-9A-Za-z_-]{11})$')
    ]
    for pattern in idpatterns:
        match = pattern.search(source)
        if match:
            return match.group(1)
    print(f'Error: unable to get ID from "{source}"!')
    sys.exit(1)

if len(sys.argv) != 2:
    print("Error: incorrect usage!")
    sys.exit(1)
ytid = getid(sys.argv[1])


ytmusic = call(YTMusic, oauthfile)

unplylst = call(ytmusic.get_playlist, unplylstid, limit=9999)["tracks"]
for song in unplylst:
    if song["videoId"] == ytid:
        print(f"Notice: removing [{ytid}] from 'Unliked Liked Songs'...")
        call(ytmusic.remove_playlist_items, unplylstid, [song])
        break

files = list(os.scandir(unmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    lclytid = filename.split(').')[0].split('(')[-1]
    if lclytid == ytid:
        print(f'Notice: deleting "{filename}"...')
        os.remove(file)
        break
