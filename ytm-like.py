#!/usr/bin/python

from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
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

# like
song = ytmusic.get_watch_playlist(ytid, limit=1)["tracks"][0]
if song["videoId"] != ytid:
    print("Error: something is wrong, ytid's don't match!")
    sys.exit(1)

if song["likeStatus"] != "LIKE":
    response = ytmusic.rate_song(ytid, "LIKE")
    responsetext = getresponsetext(response)
    if responsetext != "Saved to liked songs":
        print("Error: couldn't add {ytid} to liked songs!")
        print(f'The response was: "{responsetext}"')
        sys.exit(1)
else:
    print("Notice: song already liked!")

# add to library
skip = False
try:
    addtoken = song["feedbackTokens"]["add"]
    response = ytmusic.edit_song_library_status(addtoken)
except:
    skip = True
if not skip and getresponsetext(response) != "Added to library":
#   print(f'Warning: [{ytid}] got removed from library! Trying to fix...')
    addtoken = song["feedbackTokens"]["remove"]
    response = ytmusic.edit_song_library_status(addtoken)
    responsetext = getresponsetext(response)
    if responsetext != "Added to library":
        print(f"Error: couldn't add [{ytid}] to library!")
        print(f'The response was: "{responsetext}"')
        sys.exit(1)

# add to 'liked songs'
exitcode = 0
try:
    ytmusic.add_playlist_items(lkplylstid, [ytid], duplicates=False)
except Exception as e:
    exitcode = 1
    print("Warning: couldn't add [{ytid}] to 'Liked Songs'!")
    print(e)
    print()

# cleanup 'unliked liked songs'
unplylst = ytmusic.get_playlist(unplylstid, limit=9999)["tracks"]
for song in unplylst:
    if song["videoId"] == ytid:
        print(f"Notice: removing [{ytid}] from 'Unliked Liked Songs'...")
        ytmusic.remove_playlist_items(unplylstid, [song])
        break

# cleanup 'archive'
files = list(os.scandir(unmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    lclytid = filename.split(').')[0].split('(')[-1]
    if lclytid == ytid:
        print(f'Notice: "{filename}" now liked, moving to music...')
        os.rename(file, os.path.join(lkmusicdir, filename))
        sys.exit(exitcode)

# see if already downloaded
found = False
files = list(os.scandir(lkmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    lclytid = filename.split(').')[0].split('(')[-1]
    if lclytid == ytid:
        found = True
        break
if not found:
    downloadfailed = False
    # download with yt-dlp
    ydlopts = {
        'format': 'bestaudio/best',
        'outtmpl': {'default': '/media/storage/Music/%(title)s (%(id)s).%(ext)s'},
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'nopostoverwrites': False,
                            'preferredcodec': 'best',
                            'preferredquality': '0'}]
        }
    with YoutubeDL(ydlopts) as ydl:
        try:
            ydl.download([ytid])
        except Exception as e:
            print('Error: downloading failed with the following error!')
            print(e)
            sys.exit(1)
else:
    print('Notice: song already downloaded!')

sys.exit(exitcode)
