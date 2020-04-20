import sys

from privex.helpers import empty
from privex.loghelper import LogHelper

from steempeers import settings
from typing import Optional, Union
from os import path
import logging
log = logging.getLogger(__name__)


def set_log_level(level: Union[str, int]) -> logging.Logger:
    level = logging.getLevelName(str(level).upper()) if isinstance(level, str) else level
    _lh = LogHelper('steempeers', handler_level=level)
    _lh.add_console_handler()
    return _lh.get_logger()


def find_geoip() -> Optional[str]:
    for p in settings.search_geoip:
        ga, gc = path.join(p, settings.GEOASN_NAME), path.join(p, settings.GEOCITY_NAME)
        log.debug("Checking if %s exists...", ga)
        log.debug("Checking if %s exists...", gc)
        if path.exists(ga) and path.exists(gc):
            log.debug("Both files exist in path: %s", p)
            return p
    return None


def err(*args, file=sys.stderr, **kwargs):
    print(*args, file=file, **kwargs)


def detect_geoip(geoasn: str, geocity: str):
    if path.exists(geoasn) and path.exists(geocity):
        return geoasn, geocity
    
    log.warning("Couldn't find GeoIP ASN / City in folder %s - checking for alternative GeoIP folders...", settings.GEOIP_DIR)
    log.warning("Search paths: %s", settings.search_geoip)
    new_geodir = find_geoip()
    
    if empty(new_geodir):
        log.error("Failed to locate GeoIP ASN + City in alternative search folders.")
        err(f" [!!!] ERROR - Missing GeoIP files. The following files do not exist:\n")
        if not path.exists(geoasn):
            err(f"\t{geoasn}")
        if not path.exists(geocity):
            err(f"\t{geocity}")
        err(f"\nCurrent environment settings for GeoIP location:\n")
        
        err(f"GEOIP_DIR={settings.GEOIP_DIR}")
        err(f"GEOASN_NAME={settings.GEOASN_NAME}")
        err(f"GEOCITY_NAME={settings.GEOCITY_NAME}\n")
        
        err("Please download the GeoLite2 City and ASN GeoIP databases (Maxmind Binary Database format) from the following URL:\n")
        err("\thttps://dev.maxmind.com/geoip/geoip2/geolite2/\n")
        err("If you have the GeoIP2 databases installed in an alternative location, please insert/update the correct location")
        err("and file names using the environmental variables above - within your steem-peers .env file.\n\n")
        err(" [!!!] Falling back to basic functionality - cannot determine ISP / Country without GeoIP databases.\n\n")
        settings.USE_GEOIP = False
        return None, None

    log.info("Found GeoIP installation at folder: %s", new_geodir)
    settings.GEOIP_DIR = new_geodir
    
    geocity, geoasn = path.join(settings.GEOIP_DIR, settings.GEOCITY_NAME), path.join(settings.GEOIP_DIR, settings.GEOASN_NAME)
    log.info("GeoIP ASN: %s", geoasn)
    log.info("GeoIP City: %s\n", geocity)
    log.info("To avoid this warning in the future, add the following to your .env file at %s :\n", path.join(settings.BASE_DIR, '.env'))
    print(f"\tGEOIP_DIR={settings.GEOIP_DIR}\n\n")
    return geocity, geoasn


set_log_level(settings.LOG_LEVEL)

