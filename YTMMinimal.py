from ytmusicapi import YTMusic
import os
import re
import random
import string
import sys

lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
unplylstid = "PL9cE5Kd6uzpiu0WpDfY5T4rexKsYoa4E7"
lkmusicdir = "/media/storage/Music"
unmusicdir = "/media/storage/Music/archive"

ytmusic = YTMusic("/home/ashish/.config/ytmusic-oauth.json")

lcllkytids = []
files = list(os.scandir(lkmusicdir))
for file in files:
    if os.path.isfile(os.path.join(lkmusicdir, file)):
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        lcllkytids.append(ytid)
lclunytids = []
files = list(os.scandir(unmusicdir))
for file in files:
    if os.path.isfile(os.path.join(unmusicdir, file)):
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        lclunytids.append(ytid)