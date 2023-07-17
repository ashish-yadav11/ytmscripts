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


def onlylocal(remotesongytids, localmusicdir):
    files = os.scandir(localmusicdir)
    localfiles = []
    localytids = []
    for file in files:
        if not file.is_file():
            continue
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        if ytid not in remotesongytids:
            localytids.append(ytid)
            localfiles.append(file)
    numlocalytids = len(localytids)
    for i in range(numlocalytids):
        file = localfiles[i]
        ytid = localytids[i]
        print(i+1, numlocalytids, file.name)
        print(f'\thttps://music.youtube.com/watch?v={ytid}\thttps://www.youtube.com/watch?v={ytid}')
        rm = input("Delete file? [Y/n]: ")
        rm = rm.strip()
        if rm != 'n' and rm != 'N':
            os.remove(file)
            print("File deleted, continuing...")
        else:
            print("Continuing...")

ytmusic = YTMusic(oauthfile)

print('Liked Songs...')
lksongs_p = ytmusic.get_liked_songs(limit=9999)["tracks"]
lksongs = filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p)
lkytids = [song["videoId"] for song in lksongs]
onlylocal(lkytids, lkmusicdir)

print('Unliked Liked Songs...')
unsongs = ytmusic.get_playlist(unplylstid, limit=9999)["tracks"]
unytids = [song["videoId"] for song in unsongs]
onlylocal(unytids, unmusicdir)
