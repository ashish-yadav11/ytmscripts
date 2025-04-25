#!/bin/sh
oauthfile="/home/ashish/.config/youtube-oauth.json"
tokenrefresh="ytb-tokenRefresh"

case "$#" in
    1) url="$1" ;;
    *) echo "Usage: ytb-isLiked [url]" >&2; exit 2 ;;
esac
if ! echo "$url" | grep -qm1 \
        "^https://\(music\|www\)\.youtube\.com/watch?v=...........\($\|&\)" ; then
    echo "Error: invalid url!" >&2
    exit 2
fi
url="${url%%&*}"
vid="${url##*"/watch?v="}"

readoauthfile() {
    read -r token <"$oauthfile"
    accesstoken="${token#*'"token": "'}"
    accesstoken="${accesstoken%%'", "'*}"
    expiresat="${token##*'"expiry": "'}"
    expiresat="${expiresat%'"}'*}"
    expiresat="$(date "+%s" --date="$expiresat")"
}

readoauthfile
if [ "$(( expiresat - 10 ))" -lt "$(date +%s)" ] ; then
    if ! $tokenrefresh ; then
        echo "Error: something went wrong while refreshing access token!" >&2
        exit 2
    fi
    readoauthfile
fi

if ! output="$(curl -s "https://youtube.googleapis.com/youtube/v3/videos/getRating?id=$vid" \
                --header "Authorization: Bearer $accesstoken")" ; then
    echo "Error: something went wrong with curl!" >&2
    exit 2
fi

if echo "$output" | grep -qm1 '"rating": "like"' ; then
    echo 1
    exit 0
elif echo "$output" | grep -qm1 '"rating": "' ; then
    echo 0
    exit 1
else
    echo "Error: something went wrong with curl!" >&2
    echo "curl output:" >&2
    echo "$output" >&2
    exit 2
fi
