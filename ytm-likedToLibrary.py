#!/usr/bin/python

from ytmusicapi import YTMusic

oauthfile = "/home/ashish/.config/ytmusic-oauth.json"


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
numlksongs = len(lksongs)
for i in range(numlksongs):
    print(i+1, numlksongs)
    song = lksongs[i]
    ytid = song["videoId"]
    if not "feedbackTokens" in song or not "remove" in song["feedbackTokens"]:
        continue
    addtoken = song["feedbackTokens"]["remove"]
    if not addtoken:
        continue
    response = call(ytmusic.edit_song_library_status, addtoken)
    if getresponsetext(response) != "Added to library":
        print(f'Warning: [{ytid}] got removed from library! Trying to fix...')
        addtoken = song["feedbackTokens"]["add"]
        response = call(ytmusic.edit_song_library_status, addtoken)
        responsetext = getresponsetext(response)
        if responsetext != "Added to library":
            print(f'Error: something went wrong while adding [{ytid}] to library!')
            print(f'The response was: "{responsetext}"')
            sys.exit(1)
