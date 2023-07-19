#!/usr/bin/python

from ytmusicapi import YTMusic
import os
import re
import random
import string
import sys

# 1. move liked songs to the 'Liked Songs' playlist (after clearing it first)
# 2. remove "now liked" songs from 'Unliked Liked Songs' playlist
# 3. move "not liked but in library" to 'Unliked Liked Songs' playlist (just appending), remove them from library
# 4. remove "now liked" songs from /media/storage/Music/archives/
# 5. add songs in /media/storage/Music/archives/ to 'Unliked Liked Songs' playlist (if they are not already there)

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


def getresponsetext(resp):
    resptext = list(resp["actions"][0]["addToToastAction"]["item"].values())[0]
    return list(resptext.values())[0]["runs"][0]["text"]

ytmusic = call(YTMusic, oauthfile)

lksongs_p = call(ytmusic.get_liked_songs, limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))
lkytids = [song["videoId"] for song in lksongs]

print("1...")
lkplylst = call(ytmusic.get_playlist, lkplylstid, limit=9999)["tracks"]
unlksongs = list(filter(lambda s: s["videoId"] not in lkytids, lkplylst))
print("Cleaning up 'Liked Songs'...")
if len(unlksongs) > 0:
    call(ytmusic.remove_playlist_items, lkplylstid, unlksongs)
lkpytids = [song["videoId"] for song in lkplylst]
lkytids_add = list(filter(lambda s: s not in lkpytids, lkytids))
# 'duplicates=False' misbehaves, and anyway 'duplicates=True' is irrelevant
# because we know there are no duplicates in lkytids_add
print("Filling up 'Liked Songs'...")
if (len(lkytids_add)):
    call(ytmusic.add_playlist_items, lkplylstid, lkytids_add, duplicates=True)


print("\n\n2...")
unplylst = call(ytmusic.get_playlist, unplylstid, limit=9999)["tracks"]
unpytids_p = [song["videoId"] for song in unplylst]
lkunsongs = list(filter(lambda s: s["videoId"] in lkytids, unplylst))
print("Cleaning up 'Unliked Liked Songs'...")
if len(lkunsongs) > 0:
    call(ytmusic.remove_playlist_items, unplylstid, lkunsongs)
unpytids = list(filter(lambda s: s not in lkytids, unpytids_p))


print("\n\n3...")
lbalbumytids = []
lbalbums = call(ytmusic.get_library_albums, limit=9999)
for lbalbum in lbalbums:
    album = call(ytmusic.get_album, lbalbum["browseId"])["tracks"]
    lbalbumytids.extend([song["videoId"] for song in album])

lbsongs = call(ytmusic.get_library_songs, limit=9999)
notlikedlbsongs = list(filter(lambda s: s["videoId"] not in lkytids and s["videoId"] not in lbalbumytids, lbsongs))

print("Filling up 'Unliked Liked Songs'...")
numnotlikedlbsongs = len(notlikedlbsongs)
for i in range(numnotlikedlbsongs):
    print(i+1, numnotlikedlbsongs)
    song = notlikedlbsongs[i]
    ytid = song["videoId"]

    if ytid not in unpytids:
        call(ytmusic.add_playlist_items, unplylstid, [ytid], duplicates=True)
        unpytids.append(ytid)

    if not "feedbackTokens" in song or not "add" in song["feedbackTokens"]:
        print(f"Warning: [{ytid}] isn't really in library!")
        print(f'\thttps://music.youtube.com/watch?v={ytid}')
        continue
    remtoken = song["feedbackTokens"]["add"]
    if not remtoken:
        print(f"Warning: [{ytid}] isn't really in library!")
        print(f'\thttps://music.youtube.com/watch?v={ytid}')
        continue
    response = call(ytmusic.edit_song_library_status, remtoken)
    if getresponsetext(response) != "Removed from library":
        print(f'Warning: [{ytid}] got added to library! Trying to fix...')
        remtoken = song["feedbackTokens"]["remove"]
        response = call(ytmusic.edit_song_library_status, remtoken)
        responsetext = getresponsetext(response)
        if responsetext != "Removed from library":
            print(f"Error: couldn't remove [{ytid}] from library!")
            print(f'The response was: "{responsetext}"')
            sys.exit(1)


print("\n\n4...")
files = list(os.scandir(unmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    if ytid in lkytids:
        print(f'"{filename}" now liked, deleting...')
        os.remove(file)


print("\n\n5...")
files = list(os.scandir(unmusicdir))
numfiles = len(list(files))
print("Filling up 'Unliked Liked Songs' with local archive songs...")
for i in range(numfiles):
#   print(i+1, numfiles)
    file = files[i]
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    if ytid not in unpytids:
        if ytid in lbalbumytids:
            print(f'Warning: "{filename}" is in some album in the library. Are you sure it should be in archives?')
        try:
            ytmusic.add_playlist_items(unplylstid, [ytid], duplicates=True)
        except Exception as e:
            print(f'Warning: something possibly wrong with "{filename}"...')
            print(e)
            print(f'\thttps://music.youtube.com/watch?v={ytid}\thttps://www.youtube.com/watch?v={ytid}')
            continue
