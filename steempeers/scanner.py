import operator
import shlex
import subprocess
from socket import gethostbyaddr, herror
from typing import Optional, List, Tuple, Generator

import geoip2.database
from privex.helpers import DictObject, empty
from steempeers import settings
import logging

log = logging.getLogger(__name__)


class PeerScanner:
    _geo_asn: Optional[geoip2.database.Reader]
    _geo_city: Optional[geoip2.database.Reader]
    
    def __init__(self):
        self.counts, self.ip_data = DictObject(countries={}, cities={}, asn={}), {}
        self.ip_list = []
        self._geo_asn, self._geo_city = None, None
    
    @property
    def _ns_cmd(self):
        # If USE_DOCKER is True, obtain the PID of the docker container, then use nsenter
        # to run netstat inside of the containers network stack
        if settings.USE_DOCKER:
            log.debug("Getting PID for docker container '%s'", settings.DOCKER_NAME)
            cmd = shlex.split("docker inspect -f '{{.State.Pid}}' " + settings.DOCKER_NAME)
            
            with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
                pid = proc.stdout.read().decode('utf-8')
            log.debug('steemd docker pid is: %s', pid)
            return shlex.split("nsenter -t " + pid + " -n netstat -avWetn")
        # Otherwise, just a plain netstat.
        return shlex.split("netstat -avWetn")

    def _netstat(self):
        # Execute the command above, then split the output by newlines
        with subprocess.Popen(self._ns_cmd, stdout=subprocess.PIPE) as proc:
            data = proc.stdout.read().decode('utf-8')
        # Split the output by newlines and remove the Netstat headers
        return data.split('\n')[2:]

    def netstat(self, data: List[str] = None) -> List[str]:
        ip_list = []
        data = self._netstat() if empty(data) else data
        
        # --- Loop over each line of the netstat output and parse/filter it ---
        for line in data:
            try:
                # 4th column contains remote host, remove port by splitting
                ip_port = line.split()[4]
                # Remove the port number, and support IPv6 addresses by first splitting by :
                # then combining by : and excluding the last item (the port)
                ip = ':'.join(ip_port.split(':')[:-1])
                # Ignore Docker LAN IPs and various local bind addresses
                if ip[0:7] == '172.17.': continue
                if ip in ['0.0.0.0', '127.0.0.1', '::', '::1']: continue
                ip_list.append(ip)
            except:
                continue
        
        log.debug('IP List: %s', ip_list)
        return list(set(ip_list))
    
    @property
    def geo_city(self) -> geoip2.database.Reader:
        if not self._geo_city:
            self._geo_city = geoip2.database.Reader(settings.GEOCITY).__enter__()
        return self._geo_city

    @property
    def geo_asn(self) -> geoip2.database.Reader:
        if not self._geo_asn:
            self._geo_asn = geoip2.database.Reader(settings.GEOASN).__enter__()
        return self._geo_asn
    
    def get_asn(self, addr: str) -> Optional[str]:
        try:
            response = self.geo_asn.asn(addr)
            org = response.autonomous_system_organization
            return org
        except Exception as e:
            log.warning('Error: %s', e)
        return None

    def get_location(self, addr: str) -> Tuple[Optional[str], Optional[str]]:
        try:
            response = self.geo_city.city(addr)
            country = response.country.names.get('en', None)
            city = response.city.names.get('en', None)
            return country, city
        except Exception as e:
            log.warning('Error: %s', e)
        return None, None
    
    @staticmethod
    def get_rdns(addr: str) -> str:
        try:
            rdns = gethostbyaddr(addr)
            return rdns[0]
        except (Exception, herror):
            return 'N/A'

    def scan_ip(self, ip: str) -> DictObject:
        dt = DictObject(country="unknown", city="unknown", asn="unknown", rdns='N/A')
        dt.rdns = self.get_rdns(ip)
        
        if not settings.USE_GEOIP:
            dt.asn = dt.country = dt.city = 'NO_GEOIP_DB', 'NO_GEOIP_DB', 'NO_GEOIP_DB'
            return dt

        dt.asn = self.get_asn(ip)
        if not empty(dt.asn):
            self._bump_asn(dt.asn)
        else:
            dt.asn = "unknown"
        
        dt.country, dt.city = self.get_location(ip)
        if not empty(dt.country):
            self._bump_country(dt.country)
        else:
            dt.country = "unknown"
        
        if not empty(dt.city):
            self._bump_city(dt.city)
        else:
            dt.city = "unknown"

        return dt
    
    def scan_ips(self) -> Generator[Tuple[str, DictObject], None, None]:
        self.ip_list = self.netstat()

        for ip in self.ip_list:
            ipd = self.scan_ip(ip)
            self.ip_data[ip] = ipd
            yield (ip, ipd)
        
    def run(self):
    
        _LN = '\n----------------------\n'
        print(_LN)
        print("{:<25} {:<30} {:<30} {:<35} {}".format('IP', 'Country', 'City', 'ASN', 'rDNS'))

        for ip, ipd in self.scan_ips():
            print("{ip:<25} {country:<30} {city:<30} {asn:<35} {rdns}".format(ip=ip, **ipd))
        print()
    
        print(_LN)
    
        log.info('Total IPs: %s', len(self.ip_list))
        sorted_counts = sorted(self.counts.asn.items(), key=operator.itemgetter(1), reverse=True)
    
        log.info('Printing sorted ASNs\n')
    
        for x, y in sorted_counts:
            print(f'{x}\t{y}')
    
        print(_LN)
    
        log.info('Printing sorted countries\n')
        sorted_countries = sorted(self.counts.countries.items(), key=operator.itemgetter(1), reverse=True)
        for x, y in sorted_countries:
            print(f'{x}\t{y}')
        print()
    
        print(_LN)

    def _bump_country(self, country: str):
        if country not in self.counts.countries: self.counts.countries[country] = 0
        self.counts.countries[country] += 1

    def _bump_city(self, city: str):
        if city not in self.counts.cities: self.counts.cities[city] = 0
        self.counts.cities[city] += 1

    def _bump_asn(self, asn: str):
        if asn not in self.counts.asn: self.counts.asn[asn] = 0
        self.counts.asn[asn] += 1

    def __enter__(self):
        if settings.USE_GEOIP:
            if not self._geo_asn:
                self._geo_asn = geoip2.database.Reader(geoasn).__enter__()
            if not self._geo_city:
                self._geo_city = geoip2.database.Reader(geocity).__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._geo_asn: self._geo_asn.__exit__(exc_type=exc_type, exc_value=exc_val, traceback=exc_tb)
        if self._geo_city: self._geo_city.__exit__(exc_type=exc_type, exc_value=exc_val, traceback=exc_tb)
        
        self._geo_asn = None
        self._geo_city = None
    
    def __del__(self):
        if self._geo_asn: self._geo_asn.close()
        if self._geo_city: self._geo_city.close()
        self._geo_asn = None
        self._geo_city = None
