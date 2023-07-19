#!/usr/bin/python

import sys
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


clean = False
if len(sys.argv) > 1:
    if sys.argv[1] == '-c':
        clean = True


def getresponsetext(resp):
    resptext = list(resp["actions"][0]["addToToastAction"]["item"].values())[0]
    return list(resptext.values())[0]["runs"][0]["text"]

def subscribe(channelid):
    response = call(ytmusic.subscribe_artists, [channelid])
    responsetext = getresponsetext(response)
    if responsetext != "Subscribed to ":
        print(f"Warning: couldn't subscribe to [{channelid}]")
        print(f'\thttps://music.youtube.com/channel/{channelid}')
        print(responsetext)

def unsubscribe(channelid):
    response = call(ytmusic.unsubscribe_artists, [channelid])
    responsetext = getresponsetext(response)
    if responsetext != "Unsubscribed from ":
        print(f"Warning: couldn't subscribe from [{channelid}]")
        print(f'\thttps://music.youtube.com/channel/{channelid}')
        print(responsetext)

ytmusic = call(YTMusic, oauthfile)

if clean:
    subs = call(ytmusic.get_library_subscriptions, limit=9999)
    browseids = [artist["browseId"] for artist in subs]
    numsubs = len(browseids)
    subschannelids = []
    print("Getting current subscriptions...")
    for i in range(numsubs):
        print(i+1, numsubs)
        browseid = browseids[i]
        artist = call(ytmusic.get_artist, browseid)
        if artist["subscribed"]:
            subschannelids.append(artist["channelId"])

print("Getting wanted subscriptions...")
lksongs_p = call(ytmusic.get_liked_songs, limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))
numlksongs = len(lksongs)
channelids = []
channellks = []
for i in range(numlksongs):
    artists = lksongs[i]["artists"]
    for artist in artists:
        artistid = artist["id"]
        if not artistid:
            continue
        if artistid in channelids:
            idx = channelids.index(artistid)
            channellks[idx] += 1
        else:
            channelids.append(artistid)
            channellks.append(1)
if clean:
    wsubschannelids = []
    numchannels = len(channelids)
    for i in range(numchannels):
        if channellks[i] > 1:
            wsubschannelids.append(channelids[i])

    print("Cleaning up subscriptions...")
    for channelid in subschannelids:
        if channelid not in wsubschannelids:
            unsubscribe(channelid)
    print("Filling up subscriptions...")
    for channelid in wsubschannelids:
        if channelid not in subschannelids:
            subscribe(channelid)
else:
    numchannels = len(channelids)
    print("Filling up subscriptions...")
    for i in range(numchannels):
        if channellks[i] > 1:
            subscribe(channelids[i])
