from ytmusicapi import YTMusic
import os
import sys

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"
lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
unplylstid = "PL9cE5Kd6uzpiu0WpDfY5T4rexKsYoa4E7"
lkmusicdir = "/media/storage/Music"
unmusicdir = "/media/storage/Music/archive"


ytmusic = YTMusic(oauthfile)

lcllkytids = []
files = list(os.scandir(lkmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    lcllkytids.append(ytid)
lclunytids = []
files = list(os.scandir(unmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    lclunytids.append(ytid)
