#!/usr/bin/env bash
######################################
# GeoIP Update Script
# Part of https://github.com/someguy123/steem-peers
#
# License: AGPL v3
# (C) 2019 Someguy123 / Privex Inc.
######################################

k=(ASN Country City)

cd /tmp
mkdir -p /usr/local/var/GeoIP

echo "Removing old GeoLites from /tmp"
rm -rv GeoLite2-*
echo "Downloading new GeoLite's: ${k[@]}"
for i in ${k[@]}; do
    echo " >> downloading GeoLite $i"
    wget -q http://geolite.maxmind.com/download/geoip/database/GeoLite2-${i}.tar.gz
    echo " >> extracting GeoLite $i"
    tar xf GeoLite2-${i}.tar.gz
    echo " >> installing GeoLite $i"
    cp -v GeoLite2-${i}_*/GeoLite2-${i}.mmdb /usr/local/var/GeoIP/
done

