from ytmusicapi import YTMusic, OAuthCredentials
import json
import os
import sys

credsfile = "/home/ashish/.config/ytmusic-creds.json"
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

with open(credsfile, 'r') as f: creds = json.load(f)["installed"]
ytmusic = call(
    YTMusic,
    oauthfile,
    oauth_credentials=OAuthCredentials(
        **{k: creds[k] for k in ("client_id", "client_secret")}
    )
)

lcllkytids = []
files = list(os.scandir(lkmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    lcllkytids.append(ytid)
lclunytids = []
files = list(os.scandir(unmusicdir))
for file in files:
    if not file.is_file():
        continue
    filename = file.name
    ytid = filename.split(').')[0].split('(')[-1]
    lclunytids.append(ytid)
