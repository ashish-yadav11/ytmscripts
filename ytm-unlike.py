#!/usr/bin/python

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


def getresponsetext(resp):
    resptext = list(resp["actions"][0]["addToToastAction"]["item"].values())[0]
    return list(resptext.values())[0]["runs"][0]["text"]

# unlike
song = ytmusic.get_watch_playlist(ytid, limit=1)["tracks"][0]
if song["videoId"] != ytid:
    print("Error: something is wrong, ytid's don't match!")
    sys.exit(1)

if song["likeStatus"] == "LIKE":
    response = ytmusic.rate_song(ytid, "INDIFFERENT")
    responsetext = getresponsetext(response)
    if responsetext != "Removed from your likes":
        print("Error: couldn't remove [{ytid}] from liked songs!")
        print(f'The response was: "{responsetext}"')
        sys.exit(1)
else:
    print("Notice: song already not liked!")
    sys.exit(0)

# remove from library
isvideo = False
try:
    remtoken = song["feedbackTokens"]["remove"]
    response = ytmusic.edit_song_library_status(remtoken)
except:
    isvideo = True
if not isvideo and getresponsetext(response) != "Removed from library":
    print(f'Warning: [{ytid}] got added to library! Trying to fix...')
    remtoken = song["feedbackTokens"]["add"]
    response = ytmusic.edit_song_library_status(remtoken)
    if getresponsetext(response) != "Removed from library":
        print(f'Retrying...')
        remtoken = song["feedbackTokens"]["remove"]
        response = ytmusic.edit_song_library_status(remtoken)
        responsetext = getresponsetext(response)
        if responsetext != "Removed from library":
            print(f'Error: something went wrong while removing [{ytid}] from library!')
            print(f'The response was: "{responsetext}"')
            sys.exit(1)

# cleanup 'liked songs'
lkplylst = ytmusic.get_playlist(lkplylstid, limit=9999)["tracks"]
for song in lkplylst:
    if song["videoId"] == ytid:
        print(f"Notice: removing [{ytid}] from 'Liked Songs'...")
        ytmusic.remove_playlist_items(lkplylstid, [song])
        break

# cleanup 'music'
files = list(os.scandir(lkmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    lclytid = filename.split(').')[0].split('(')[-1]
    if lclytid == ytid:
        print(f'Notice: "{filename}" now not liked, moving to archive...')
        os.rename(file, os.path.join(unmusicdir, filename))
        # add to 'unliked liked songs'
        try:
            ytmusic.add_playlist_items(unplylstid, [ytid], duplicates=False)
        except Exception as e:
            print("Warning: couldn't add [{ytid}] to 'Liked Songs' playlist!")
            print(e)
            print()
            sys.exit(1)
        break

sys.exit(0)
