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


ytmusic = call(YTMusic, oauthfile)

subs = call(ytmusic.get_library_subscriptions, limit=9999)
browseids = [artist["browseId"] for artist in subs]
numsubs = len(browseids)
subschannelids = []
print("Getting current subscriptions...")
for i in range(numsubs):
    print(i+1, numsubs)
    browseid = browseids[i]
    channelid = call(ytmusic.get_artist, browseid)["channelId"]
    subschannelids.append(channelid)

lksongs_p = call(ytmusic.get_liked_songs, limit=9999)["tracks"]
lksongs = list(filter(lambda s: s["likeStatus"] == "LIKE", lksongs_p))
numlksongs = len(lksongs)
channelids = []
channellks = []
print("Getting wanted subscriptions...")
for i in range(numlksongs):
    print(i+1, numlksongs)
    artists = lksongs[i]["artists"]
    for artist in artists:
        artistid = artist["id"]
        if artistid in channelids:
            idx = channelids.index(artistid)
            channellks[idx] += 1
        else:
            channelids.append(artistid)
            channellks.append(1)
wsubschannelids = []
numchannels = len(channelids)
for i in range(numchannels):
    if channellks[i] > 1:
        wsubschannelids.append(channelids[i])

print("Cleaning up subscriptions...")
usubschannelids = list(filter(lambda i: i not in wsubschannelids, subschannelids))
if len(usubschannelids) > 0:
    call(ytmusic.unsubscribe_artists, usubschannelids)
print("Filling up subscriptions...")
tsubschannelids = list(filter(lambda i: i not in subschannelids, wsubschannelids))
if len(tsubschannelids) > 0:
    call(ytmusic.subscribe_artists, tsubschannelids)
