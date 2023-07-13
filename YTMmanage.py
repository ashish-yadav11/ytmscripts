from ytmusicapi import YTMusic
import os
import re
import random
import string
import sys

# 1. moves liked songs to the 'Liked Songs' playlist (after clearing it first)
# 2. remove "now liked" songs from 'Unliked Liked Songs' playlist
# 3. moves "not liked but in library" to 'Unliked Liked Songs' playlist (just appending), removes them from library
# 4. remove "now liked" songs from /media/storage/Music/archives/
# 5. adds songs in /media/storage/Music/archives/ to 'Unliked Liked Songs' playlist (if they are not already there)

lkplylstid = "PL9cE5Kd6uzpgUN5jZDyX1RvU6wQRt4co3"
unplylstid = "PL9cE5Kd6uzpiu0WpDfY5T4rexKsYoa4E7"
#lkmusicdir = "/media/storage/Music"
unmusicdir = "/media/storage/Music/archive"

ytmusic = YTMusic("/home/ashish/.config/ytmusic-oauth.json")


def responsetext(response):
    return response["actions"][0]["addToToastAction"]["item"][
            "notificationActionRenderer"]["responseText"]["runs"][0]["text"]

lksongs_p = ytmusic.get_liked_songs(limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))
lkytids = [song["videoId"] for song in lksongs]

print("1...")
lkplylst = ytmusic.get_playlist(lkplylstid, limit=9999)["tracks"]
lenlkplylst = len(lkplylst)
step = 100
num = 0
while num < lenlkplylst:
    print(num, lenlkplylst)
    ytmusic.remove_playlist_items(lkplylstid, lkplylst[num:num+step])
    num += step
# 'duplicates=False' misbehaves, and anyway 'duplicates=True' is irrelevant
# because we have emptied the playlist and we know there are not duplicates in
# lkytids
lenlkytids = len(lkytids)
num = 0
while num < lenlkytids:
    print(num, lenlkytids)
    ytmusic.add_playlist_items(lkplylstid, lkytids[num:num+step], duplicates=True)
    num += step


print("\n\n2...")
unplylst = ytmusic.get_playlist(unplylstid, limit=9999)["tracks"]
unytids_p = [song["videoId"] for song in unplylst]
nowlikedsongs = list(filter(lambda s: s["videoId"] in lkytids, unplylst))
if len(nowlikedsongs) > 0:
    ytmusic.remove_playlist_items(unplylstid, nowlikedsongs)
unytids = list(filter(lambda s: s not in lkytids, unytids_p))


print("\n\n3...")
lbalbumytids = []
lbalbums = ytmusic.get_library_albums(limit=9999)
for lbalbum in lbalbums:
    album = ytmusic.get_album(lbalbum["browseId"])["tracks"]
    lbalbumytids.extend([song["videoId"] for song in album])

lbsongs = ytmusic.get_library_songs(limit=9999)
notlikedlbsongs = list(filter(lambda s: s["videoId"] not in lkytids and s["videoId"] not in lbalbumytids, lbsongs))

numnotlikedlbsongs = len(notlikedlbsongs)
for i in range(numnotlikedlbsongs):
    print(i+1, numnotlikedlbsongs)
    song = notlikedlbsongs[i]
    ytid = song["videoId"]

    if ytid not in unytids:
        ytmusic.add_playlist_items(unplylstid, [ytid], duplicates=True)
        unytids.append(ytid)

    try:
        remtoken = song["feedbackTokens"]["add"]
        response = ytmusic.edit_song_library_status(remtoken)
    except:
        print(f'[{ytid}] not really in the library!')
        print(f'\thttps://music.youtube.com/watch?v={ytid}')
        continue
    if responsetext(response) != "Removed from library":
        print(f'[{ytid}] The song got removed from the library! Trying to fix.')
        remtoken = song["feedbackTokens"]["remove"]
        response = ytmusic.edit_song_library_status(remtoken)
        if responsetext(response) != "Removed from library":
            print(f'[{ytid}] Some error occured, exiting...')
            sys.exit(1)


print("\n\n4...")
files = list(os.scandir(unmusicdir))
for file in files:
    if os.path.isfile(os.path.join(unmusicdir, file)):
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        if ytid in lkytids:
            print(f'"{filename}" now liked, deleting...')
            os.remove(file)


print("\n\n5...")
files = list(os.scandir(unmusicdir))
numfiles = len(list(files))
for i in range(numfiles):
#   print(i+1, numfiles)
    file = files[i]
    if os.path.isfile(os.path.join(unmusicdir, file)):
        filename = file.name
        ytid = filename.split(').')[0].split('(')[-1]
        if ytid not in unytids:
            if ytid in lbalbumytids:
                print(f'[{ytid}] "{filename}" is in some album in the library. Are you sure it should be in archives!')
            try:
                ytmusic.add_playlist_items(unplylstid, [ytid], duplicates=True)
            except Exception as e:
                print(f'[{ytid}] something is wrong with "{filename}"')
                print(e)
                print(f'\thttps://music.youtube.com/watch?v={ytid}\thttps://www.youtube.com/watch?v={ytid}')
                continue
