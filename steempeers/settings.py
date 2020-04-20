from dotenv import load_dotenv
from privex.helpers import env_bool
from os import getenv as env, path, getcwd
from os.path import dirname, abspath

load_dotenv()

BASE_DIR = dirname(abspath(__file__))

USE_DOCKER = env_bool('USE_DOCKER', True)
USE_GEOIP = env_bool('USE_GEOIP', True)

DOCKER_NAME = env('DOCKER_NAME', 'seed')

LOG_LEVEL = env('LOG_LEVEL', 'INFO')
GEOIP_DIR = env('GEOIP_DIR', '/usr/share/GeoIP')
GEOASN_NAME = env('GEOASN_NAME', 'GeoLite2-ASN.mmdb')
GEOCITY_NAME = env('GEOCITY_NAME', 'GeoLite2-City.mmdb')

GEOCITY, GEOASN = path.join(GEOIP_DIR, GEOCITY_NAME), path.join(GEOIP_DIR, GEOASN_NAME)

search_geoip = [
    '/usr/share/GeoIP',
    '/usr/lib/GeoIP',
    '/var/lib/GeoIP',
    '/usr/local/share/GeoIP',
    '/usr/local/var/GeoIP',
    '/var/GeoIP',
    path.join(getcwd(), 'GeoIP'),
    path.expanduser('~/GeoIP'),
    path.expanduser('~/.GeoIP'),
]
