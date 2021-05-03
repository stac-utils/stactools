#!/usr/bin/env sh

# This test script is a little long to run as a part of CI, but is a useful
# one-off check to make sure we can create stac items from a set of products.

set -ex

if [ "$#" -ne 2 ]; then
    echo "USAGE: $0 URLFILE OUTDIR"
    exit 1
fi

urlfile="$1"
outdir="$2"

mkdir -p $outdir

while read url; do
    scripts/stac goes create-item --cogify $url $outdir
done < $urlfile