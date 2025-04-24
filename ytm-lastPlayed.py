#!/usr/bin/python

from ytmusicapi import YTMusic, OAuthCredentials
import json

credsfile = "/home/ashish/.config/ytmusic-creds.json"
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


with open(credsfile, 'r') as f: creds = json.load(f)["installed"]
ytmusic = call(
    YTMusic,
    oauthfile,
    oauth_credentials=OAuthCredentials(
        **{k: creds[k] for k in ("client_id", "client_secret")}
    )
)
lastsong = call(ytmusic.get_history)[0]
print(f'https://music.youtube.com/watch?v={lastsong["videoId"]}|{lastsong["title"]}')
