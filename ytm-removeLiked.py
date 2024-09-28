#!/usr/bin/python

import re
import sys
from ytmusicapi import YTMusic

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"
lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
lkmusicdir = "/media/storage/Music"


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


unlikeresponses = [
    "Removed from your likes",
    "Removed from liked music",
    "Got it, we'll tune your recommendations"
]

def getresponsetext(resp):
    resptext = list(resp["actions"][0]["addToToastAction"]["item"].values())[0]
    return list(resptext.values())[0]["runs"][0]["text"]

ytmusic = call(YTMusic, oauthfile)

# unlike
song = call(ytmusic.get_watch_playlist, ytid, limit=1)["tracks"][0]
if song["videoId"] != ytid:
    print("Error: something is wrong, ytid's don't match!")
    sys.exit(1)

if song["likeStatus"] == "LIKE":
    response = call(ytmusic.rate_song, ytid, "INDIFFERENT")
    responsetext = getresponsetext(response)
    if responsetext not in unlikeresponses:
        print("Error: couldn't remove [{ytid}] from liked songs!")
        print(f'The response was: "{responsetext}"')
        sys.exit(1)

# remove from library
if "feedbackTokens" in song and song["feedbackTokens"] and "add" in song["feedbackTokens"]:
    remtoken = song["feedbackTokens"]["add"]
    if remtoken:
        response = call(ytmusic.edit_song_library_status, remtoken)
        if getresponsetext(response) != "Removed from library":
            print(f'Warning: [{ytid}] got added to library! Trying to fix...')
            remtoken = song["feedbackTokens"]["remove"]
            response = call(ytmusic.edit_song_library_status, remtoken)
            responsetext = getresponsetext(response)
            if responsetext != "Removed from library":
                print(f'Error: something went wrong while removing [{ytid}] from library!')
                print(f'The response was: "{responsetext}"')
                sys.exit(1)

# clean up 'liked songs'
lkplylst = call(ytmusic.get_playlist, lkplylstid, limit=9999)["tracks"]
for song in lkplylst:
    if song["videoId"] == ytid:
        print(f"Notice: removing [{ytid}] from 'Liked Songs'...")
        call(ytmusic.remove_playlist_items, lkplylstid, [song])
        break

# clean up 'music'
files = list(os.scandir(lkmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    lclytid = filename.split(').')[0].split('(')[-1]
    if lclytid == ytid:
        print(f'Notice: deleting "{filename}"...')
        os.remove(file)
