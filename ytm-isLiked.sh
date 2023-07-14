#!/bin/sh
oauthfile="/home/ashish/.config/ytmusic-oauth.json"
ytmauthhack_script="ytm-authorizationHack"

case "$#" in
    1) url="$1" ;;
    *) echo "Usage: ytm-isLiked [url]"; exit 2 ;;
esac
if ! echo "$url" | grep -qm1 \
        "^https://\(music\|www\)\.youtube\.com/watch?v=...........\($\|&\)" ; then
    echo "Error: invalid url!"
    exit 2
fi
url="${url%%&*}"
vid="${url##*"/watch?v="}"

readoauthfile() {
    {
        read -r dummy
        read -r accesstoken
        read -r dummy; read -r dummy; read -r dummy; read -r dummy
        read -r expiresat
    } <"$oauthfile"
    accesstoken="${accesstoken%\"*}"
    accesstoken="${accesstoken##*': "'}"
    expiresat="${expiresat##*": "}"
}

readoauthfile
if [ "$(( expiresat - 1 ))" -lt "$(date +%s)" ] ; then
    echo "Notice: doing authorization hack!"
    $ytmauthhack_script
    readoauthfile
fi

if ! output="$(curl -s "https://youtube.googleapis.com/youtube/v3/videos/getRating?id=$vid" \
                --header "Authorization: Bearer $accesstoken")" ; then
    echo "Error: something went wrong!"
    exit 2
fi

if echo "$output" | grep -qm1 '"rating": "like"' ; then
    echo 1
    exit 0
elif echo "$output" | grep -qm1 '"rating": "' ; then
    echo 0
    exit 1
else
    echo "Error: something went wrong!"
    echo "curl output:"
    echo "$output"
    exit 2
fi
