from ytmusicapi import YTMusic
import json
import os
import sys

brwsrfile = "/home/ashish/.config/ytmusic-brwsr.json"
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

ytmusic = call(YTMusic, brwsrfile)

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
