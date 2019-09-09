Steem Peers Scanner - A small Python 3 script for analyzing the peers connected to a Steem node

**Copyright:** (C) 2019   Someguy123 https://github.com/someguy123

**License:** AGPL v3

```
+===================================================+
|                 © 2019 Someguy123                 |
|           https://github.com/someguy123           |
+===================================================+
|                                                   |
|        Steem Peers Scanner                        |
|                                                   |
|        Core Developer(s):                         |
|                                                   |
|          (+)  Chris (@someguy123) [Privex]        |
|                                                   |
+===================================================+
```

Install / Usage
===============

```sh
# Install python3.7 and pip
sudo apt update -y
sudo apt install -y python3.7 python3.7-dev python3-pip

# Clone the repo
git clone https://github.com/someguy123/steem-peers.git
cd steem-peers

# Install requirements (using python3.7)
sudo -H python3.7 -m pip install -r requirements.txt
# Download/update GeoIP databases
sudo ./update_geoip.sh

# Scan peers. If no env options configured, will get peers from docker container `seed`
sudo ./peers.py
```

Environment Options (place in .env or pass on command line)
===============================

 - **USE_DOCKER**  (Def: true) - Boolean (true/false/1/0)
    - true  = scan peers inside of docker container `$DOCKER_NAME`
    - false = scan peers on the host running this script
 - **DOCKER_NAME** (Def: seed) - String
    - If USE_DOCKER is true, this is the name of the container to scan peers inside

