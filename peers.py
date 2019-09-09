#!/usr/bin/env python3.7
######################################
# Steem Peers Scanner - Main Python Script 
# Part of https://github.com/someguy123/steem-peers
#
# Usage:
#
#   sudo -H python3.7 -m pip install -r requirements.txt
#   sudo ./update_geoip.sh
#   sudo ./peers.py
#
#
# Environment Options (place in .env or pass on command line):
#
#     USE_DOCKER  [true] - Boolean (true/false/1/0) - true  = scan peers inside of docker container $DOCKER_NAME 
#                                                   - false = scan peers on the host running this script
#
#     DOCKER_NAME [seed] - String - If USE_DOCKER is true, this is the name of the container to scan peers inside
#
# License: AGPL v3
# (C) 2019 Someguy123 / Privex Inc.
######################################

import geoip2.database
import sys
import subprocess
import shlex
import operator
import time
import logging
from dotenv import load_dotenv
from socket import gethostbyaddr, herror
from privex.helpers import env_bool
from privex.loghelper import LogHelper
from os import getenv as env

load_dotenv()

use_docker = env_bool('USE_DOCKER', True)
docker_name = env('DOCKER_NAME', 'seed')

_lh = LogHelper('privex.steempeers', handler_level=logging.DEBUG)
_lh.add_console_handler()

log = _lh.get_logger()

# If USE_DOCKER is True, obtain the PID of the docker container, then use nsenter
# to run netstat inside of the containers network stack
if use_docker:
    cmd = shlex.split("docker inspect -f '{{.State.Pid}}' " + docker_name)

    pid = ""
    # print(cmd)
    with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
        pid = proc.stdout.read().decode('utf-8')
    log.debug('steemd docker pid is: %s', pid)
    cmd = shlex.split("nsenter -t " + pid + " -n netstat -avWetn")
else:
    # Otherwise, just a plain netstat.
    cmd = shlex.split("netstat -avWetn")

# Execute the command above, then split the output by newlines
data = ""
with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
    data = proc.stdout.read().decode('utf-8')
data = data.split('\n')

# Remove the Netstat headers
data = data[2:]

counts, countries, ip_data = {}, {}, {}
ip_list = []

# --- Loop over each line of the netstat output and parse/filter it ---
for line in data:
    try:
        # 4th column contains remote host, remove port by splitting
        ip_port = line.split()[4]
        # Remove the port number, and support IPv6 addresses by first splitting by :
        # then combining by : and excluding the last item (the port)
        ip = ':'.join(ip_port.split(':')[:-1])
        # Ignore Docker LAN IPs and wildcard 0.0.0.0
        if ip[0:7] == '172.17.': continue
        if ip == '0.0.0.0': continue
        ip_list.append(ip)
        ip_data[ip] = dict(country="unknown", asn="unknown")
    except:
        continue



ip_list = list(set(ip_list))
log.debug('IP List: %s', ip_list)

# --- Lookup ASN (ISP / Organization) for each peer ---
log.info('Loading ASNs for IP list...')
with geoip2.database.Reader('/usr/local/var/GeoIP/GeoLite2-ASN.mmdb') as reader:
    for ip in ip_list:
        try:
                response = reader.asn(ip)
                org = response.autonomous_system_organization
                ip_data[ip]['asn'] = org
                if org not in counts:
                    counts[org] = 0
                counts[org] += 1
        except Exception as e:
            log.warning('Error: %s', e)

# --- Lookup country of each peer ---
log.info('Loading countries for IP list...')
with geoip2.database.Reader('/usr/local/var/GeoIP/GeoLite2-City.mmdb') as reader:
    for ip in ip_list:
        try:
            response = reader.city(ip)
            #print(response.city.names['en'])
            country = response.country.names['en']
            ip_data[ip]['country'] = country
            if country not in countries:
                countries[country] = 0
            countries[country] += 1
        except Exception as e:
            log.warning('Error: %s', e)

# --- Get reverse DNS for each peer ---
log.info('Loading reverse DNS for IP list...')
for ip in ip_list:
    try:
        rdns = gethostbyaddr(ip)
        ip_data[ip]['rdns'] = rdns[0]
    except (Exception, herror) as e:
        ip_data[ip]['rdns'] = 'N/A'



log.info('----------------------')
for ip, ipd in ip_data.items():
    print("{ip:<25} {country:<30} {asn:<35} {rdns}".format(ip=ip, **ipd))

log.info('----------------------')

log.info('Total IPs: %s', len(ip_list))
sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)

log.info('Printing sorted ASNs')
for x,y in sorted_counts:
    print('{}\t{}'.format(x,y))

log.info('----------------------')

log.info('Printing sorted countries')
sorted_countries = sorted(countries.items(), key=operator.itemgetter(1), reverse=True)
for x,y in sorted_countries:
    print('{}\t{}'.format(x,y))

log.info('----------------------')
