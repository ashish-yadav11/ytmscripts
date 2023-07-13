from ytmusicapi import YTMusic
import re
import random
import string

ytmusic = YTMusic("/home/ashish/.config/ytmusic-oauth.json")


def responsetext(response):
    return response["actions"][0]["addToToastAction"]["item"][
            "notificationActionRenderer"]["responseText"]["runs"][0]["text"]

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
    if responsetext(response) != "Added to library":
        print(f'[{ytid}] The song got removed from library! Trying to fix...')
        addtoken = song["feedbackTokens"]["add"]
        response = ytmusic.edit_song_library_status(addtoken)
        if responsetext(response) != "Added to library":
            print(f'[{ytid}] Something went wrong!')
            sys.exit(1)
