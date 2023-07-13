from ytmusicapi import YTMusic
import re
import random
import string

ytmusic = YTMusic("/home/ashish/.config/ytmusic-oauth.json")


def getresponsetext(resp):
    resptext = list(resp["actions"][0]["addToToastAction"]["item"].values())[0]
    return list(resptext.values())[0]["runs"][0]["text"]

lksongs_p = ytmusic.get_liked_songs(limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))

numlksongs = len(lksongs)
for i in range(numlksongs):
    print(i+1, numlksongs)
    song = lksongs[i]
    ytid = song["videoId"]
    try:
        addtoken = song["feedbackTokens"]["remove"]
        response = ytmusic.edit_song_library_status(addtoken)
    except:
        continue
    if getresponsetext(response) != "Added to library":
        print(f'Warning: [{ytid}] got removed from library! Trying to fix...')
        addtoken = song["feedbackTokens"]["add"]
        response = ytmusic.edit_song_library_status(addtoken)
        if getresponsetext(response) != "Added to library":
            print(f'Error: something went wrong while adding [{ytid}] to library!')
            sys.exit(1)
