#!/usr/bin/env python3

import urllib.request
import json
import os, sys
import re
import getopt
import subprocess
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
# from gcmap import GCMapper
# gcm = GCMapper()



def getLoc(IP):
    "Turn a string representing an IP address into a lat long pair"
    #Other geolocation services are available
    url = "https://geolocation-db.com/json/"+IP
    response = urllib.request.urlopen(url)
    encoding = response.info().get_content_charset('utf8')
    data = json.loads(response.read().decode(encoding))
    #print(data)
    try:
        lat= float(data["latitude"])
        lon= float(data["longitude"])
        #country = data["country_name"]
        country = data["country_code"]
        city = data["city"]
        if not city:
            country = data["country_name"]
        if lat == 0.0 and lon == 0.0:
            return (None, None, None, None)
        return (lat,lon, country, city)
    except:
        return (None,None, None, None)

def printHelp():
    print ("./vis_route.py IPv4Address")
    print (" e.g. ./vis_route.py 213.138.111.222")

try:
    opts, args = getopt.getopt(sys.argv,"h")
except getopt.GetoptError:
    printHelp()
    sys.exit()
for opt, arg in opts:
    if opt == '-h':
        printHelp()
        sys.exit()
if len(args) != 2:
    printHelp()
    sys.exit()
IP= args[1]



ax = plt.axes(projection=ccrs.PlateCarree())
ax.stock_img()


#Start traceroute command

# proc = subprocess.Popen(["traceroute -m 25 -n "+IP], stdout=subprocess.PIPE, shell=True,universal_newlines=True)

proc = subprocess.Popen(["tracert", IP], stdout=subprocess.PIPE, shell=True,universal_newlines=True)


#Where we are coming from
lastLon= None
lastLat= None
lastCountry = ""
lastCity = ""
#Parse individual traceroute command lines
for line in proc.stdout:
    print(line,end="")
    if re.match(r"Tracing route to", line):
        continue
    splitline=line.split()
    if len(splitline) < 4:
         continue
    hopIP = ""
    for w in splitline:
        m = re.search(r"\[?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]?", w)
        if m:
            hopIP = m.group(0)
            break
    if hopIP == "":
        continue

    (lat,lon, country, city)=getLoc(hopIP)

    if (lat == None):
        continue
    if lastLat != None and (lastLat-lat + lastLon-lon) != 0.0:
        if city:
            text = city + ", " + country
        else:
            text = country
        if country == lastCountry and city == lastCity:
            text = ""
        
        plt.text(lon - 3, lat - 12, text,
                horizontalalignment='right',
                transform=ccrs.Geodetic())
        plt.plot([lon, lastLon], [lat, lastLat],
                color='blue', linewidth=2, marker='o',
                transform=ccrs.Geodetic(),
         )

    lastLat= lat
    lastLon= lon
    lastCountry = country
    lastCity = city

plt.tight_layout()
plt.show()
