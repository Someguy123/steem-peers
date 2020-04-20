Linux Peers Scanner - A small Python 3 script for analyzing the peers connected to a Linux system, with
support for viewing peers within a running Docker container.

**Copyright:** (C) 2019   Someguy123 https://github.com/someguy123

**License:** AGPL v3

```
+===================================================+
|                 © 2019 Someguy123                 |
|           https://github.com/someguy123           |
+===================================================+
|                                                   |
|        Linux/Docker Peers Scanner                 |
|                                                   |
|        Core Developer(s):                         |
|                                                   |
|          (+)  Chris (@someguy123) [Privex]        |
|                                                   |
+===================================================+
```

![Screenshot of peers.py in use](https://i.imgur.com/5nL0kXK.png)

Install / Usage
===============

First, clone the repo
```sh
# Clone the repo
git clone https://github.com/someguy123/steem-peers.git
cd steem-peers
```

An easy setup script is included at `setup.sh` for automatically installing the project's dependencies, as well as downloading + installing
the GeoIP databases.

You can install the dependencies first, or configure/install GeoIP first - the order doesn't matter. You'll need a Maxmind account (free) to
use the GeoIP auto-config + auto-install tool (see following section).

![Easy Installer](https://i.imgur.com/M6IGWgC.png)

Installing GeoIP + Automatic Updates
------------------------------------

Next, you'll need to signup for a Maxmind account if you haven't already got one, at: https://www.maxmind.com/en/geolite2/signup

Maxmind no longer makes their GeoLite GeoIP2 databases available for public download, so you need to sign up to be able to access them.

Log into Maxmind and go to the "My License Key" tab, then click "Generate new license key" (they're free!)

![](https://i.imgur.com/sxO7fg7.png)

Enter a name for the key e.g. "GeoIP Update Key", select "Yes" to the "will this be used with GeoIP Update" question, followed by "for use with geoipupdate version 3.1.1 or newer"

![](https://i.imgur.com/suv5jXC.png)

Save the account ID + license key somewhere safe

![](https://i.imgur.com/wejFSat.png)

Run `./setup.sh` - select `geoip`, and choose `both` if you haven't already installed `geoipupdate`.

Enter the account ID and license key you saved earlier at the appropriate prompts, and the script will generate a GeoIP.conf for you.

![](https://i.imgur.com/Lz8i9gT.png)

If you chose `both` at the previous menu, it will then ensure GeoIP Updater is installed, and run `geoipupdate` automatically to download
and install the GeoIP databases.

Installing dependencies
-----------------------

If you followed the previous section, you should've now been brought back to the main menu of `setup.sh`.

Simply select `install` at the menu, and it will automatically install any missing dependencies, including Python, Pip (Python package manager),
as well as install the dependencies of the project automatically using pip.

Running steem-peers
-------------------

Once you've setup GeoIP and installed the dependencies, simply run `peers.py` as root (e.g. using `sudo`) - it's required to run the script
as root if you're analyzing the peers for a docker container, while it should mostly work without root for non-docker peer analysis (but running
as root is still recommended to ensure it can see all active network connections).

```sh
# Scan peers. If no env options configured, will get peers from docker container `seed`
sudo ./peers.py

# View available CLI switches
./peers -h

# Scan peers for the docker container 'mycontainer'
sudo ./peers.py -c mycontainer

# Scan ALL open connections (excluding docker containers) to/from this system.
sudo ./peers.py -k
```


Environment Options (place in .env or pass on command line)
===============================

 - **USE_DOCKER**  (Def: true) - Boolean (true/false/1/0)
    - true  = scan peers inside of docker container `$DOCKER_NAME`
    - false = scan peers on the host running this script
 - **DOCKER_NAME** (Def: seed) - String
    - If USE_DOCKER is true, this is the name of the container to scan peers inside





