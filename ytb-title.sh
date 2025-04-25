#!/bin/sh
apikeyfile="/home/ashish/.config/youtube-apikey.txt"

case "$#" in
    1) url="$1" ;;
    *) echo "Usage: ytb-title [url]" >&2; exit 2 ;;
esac
if ! echo "$url" | grep -qm1 \
        "^https://\(music\|www\)\.youtube\.com/watch?v=...........\($\|&\)" ; then
    echo "Error: invalid url!" >&2
    exit 2
fi
url="${url%%&*}"
vid="${url##*"/watch?v="}"

read -r apikey <"$apikeyfile"

if ! title="$(curl -s "https://www.googleapis.com/youtube/v3/videos?id=$vid&key=$apikey&fields=items(snippet(title))&part=snippet")" ; then
    echo "Error: something went wrong!" >&2
    exit 1
fi
title="${title#*'"title": "'}"
title="${title%\"*}"
echo "$title"
exit 0
