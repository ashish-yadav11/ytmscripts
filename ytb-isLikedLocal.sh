#!/bin/sh
lkmusicdir="/media/storage/Music"
unmusicdir="/media/storage/Music/archive"

case "$#" in
    1) url="$1" ;;
    *) echo "Usage: ytb-isLikedLocal [url]" >&2; exit 3 ;;
esac

if ! echo "$url" | grep -qm1 \
        "^https://\(music\|www\)\.youtube\.com/watch?v=...........\($\|&\)" ; then
    echo "Error: invalid url!" >&2
    exit 3
fi
url="${url%%&*}"
vid="${url##*"/watch?v="}"

for file in "$lkmusicdir/"*" ($vid).opus" "$lkmusicdir/"*" ($vid).m4a"; do
    [ -e "$file" ] && { echo 1; exit 0 ;}
done
for file in "$unmusicdir/"*" ($vid).opus" "$lkmusicdir/"*" ($vid).m4a"; do
    [ -e "$file" ] && { echo 2; exit 1 ;}
done
echo 0; exit 2
