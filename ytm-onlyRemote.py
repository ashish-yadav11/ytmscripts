#!/usr/bin/python

from ytmusicapi import YTMusic
import os
import re
import random
import string

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"
lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
unplylstid = "PL9cE5Kd6uzpiu0WpDfY5T4rexKsYoa4E7"
lkmusicdir = "/media/storage/Music"
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


def onlyremote(localmusicdir, remotesongs):
    localytids = []
    files = os.scandir(localmusicdir)
    for file in files:
        if not file.is_file():
            continue
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        localytids.append(ytid)
    for i in range(len(remotesongs)):
        ytid = remotesongs[i]["videoId"]
        if ytid not in localytids:
            print(remotesongs[i]["title"])
            print(f'\thttps://music.youtube.com/watch?v={ytid}\thttps://www.youtube.com/watch?v={ytid}')

ytmusic = call(YTMusic, oauthfile)

print('Liked Songs...')
lksongs_p = call(ytmusic.get_liked_songs, limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))
onlyremote(lkmusicdir, lksongs)

print('Unliked Liked Songs...')
unsongs = call(ytmusic.get_playlist, unplylstid, limit=9999)["tracks"]
onlyremote(unmusicdir, unsongs)
