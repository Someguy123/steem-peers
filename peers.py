#!/usr/bin/env python3
######################################
# Steem Peers Scanner - Main Python Script 
# Part of https://github.com/someguy123/steem-peers
#
# Usage:
#
#   sudo -H pip3 install -r requirements.txt
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
# (C) 2020 Someguy123 / Privex Inc.
######################################

import sys
from dotenv import load_dotenv
from privex.helpers import ErrHelpParser
from os import path
from steempeers import settings
from steempeers.core import set_log_level, detect_geoip
from steempeers.scanner import PeerScanner

load_dotenv()

parser = ErrHelpParser(description='Linux Peer Scanner (C) 2020 Someguy123')

parser.add_argument('-c', '--container', default=settings.DOCKER_NAME, type=str, dest='container')
parser.add_argument('--geoip-dir', default=settings.GEOIP_DIR, type=str, dest='geoip_dir')
parser.add_argument('--geoasn', default=settings.GEOASN_NAME, type=str)
parser.add_argument('--geocity', default=settings.GEOCITY_NAME, type=str)
parser.add_argument('-l', '--log-level', default=settings.LOG_LEVEL, type=str, dest='log_level')

parser.add_argument(
    '-d', '--use-docker', action='store_true', default=settings.USE_DOCKER, dest='use_docker'
)

parser.add_argument(
    '-k', '--no-docker', action='store_false', default=settings.USE_DOCKER, dest='use_docker'
)

try:
    args = parser.parse_args()
except Exception:
    parser.error('Failed parsing arguments')
    sys.exit(1)

settings.GEOASN_NAME, settings.GEOCITY_NAME = args.geoasn, args.geocity
settings.GEOIP_DIR = args.geoip_dir[:-1] if args.geoip_dir.endswith('/') else args.geoip_dir
settings.LOG_LEVEL = args.log_level
settings.USE_DOCKER = args.use_docker
settings.DOCKER_NAME = args.container

log = set_log_level(settings.LOG_LEVEL)

settings.GEOCITY, settings.GEOASN = path.join(settings.GEOIP_DIR, settings.GEOCITY_NAME), path.join(settings.GEOIP_DIR, settings.GEOASN_NAME)
settings.GEOCITY, settings.GEOASN = detect_geoip(geoasn=settings.GEOCITY, geocity=settings.GEOASN)

PeerScanner().run()
