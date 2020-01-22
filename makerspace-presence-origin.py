#!/usr/bin/env python3
 
import json
import requests
import time
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import random
import string
import urllib.request
import shutil
 
requests.packages.urllib3.disable_warnings()
 
 
def randomString(stringLength=15):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
 
 
random = randomString()
 
 
date = datetime.today().strftime('%d.%m.%Y')
t = time.localtime()
current_time = time.strftime("%H:%M", t)
last_status = open("/home/pi/msm-status/last_status.txt", "r")
last_stat = int(last_status.read())
last_date = open("/home/pi/msm-status/date.txt", "r")
last_dateseen = str(last_date.read())
 
if last_dateseen != str(date):
    #clear csv on new day
    print("ungleiches Datum")
    activity = open("/home/pi/msm-status/activity.csv", "w")
    activity.write("")
else:
    print("continue")
 
 
print("letzte Anzahl gefundener Geraete:  " + str(last_stat))
 
api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx'
api_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
url = 'https://XXXXXXXXXXXX:XXXXXXX/api/diagnostics/interface/getArp'
# request data
r = requests.get(url,
                 verify=False,
                 auth=(api_key, api_secret))
 
list_found_macs = []
 
#data = json.load(input_file)  # get the data list
data = json.loads(r.text)
for element in data:  # iterate on each element of the list
    # element is a dict
    id = element['mac']  # get the id
#    print(id)  # print it
    list_found_macs.append(id)
 
known_macs = open('/home/pi/msm-status/known_macs.txt','r').read().split('\n')
known_macs = known_macs[:-1]
 
privacy_macs = open('/home/pi/msm-status/privacy_macs.txt','r').read().split('\n')
privacy_macs = privacy_macs[:-1]
 
 
for g in known_macs:
    #print(g)
    try:
        list_found_macs.remove(g)
    except:
        pass
 
for h in privacy_macs:
    #print(h)
    try:
        list_found_macs.remove(h)
    except:
        pass
 
 
#print(str(list_found_macs))
 
print("gefundene Geraete: " + str(len(list_found_macs)))
print("bekannte Geraete: " + str(len(known_macs)))
print("ausgeblendete Geraete: " + str(len(privacy_macs)))
print("Abfragezeit: " + str(current_time) + " " + str(date))
 
 
###################
#
#
#
#   Write to csv
   
 
 
activity = open("/home/pi/msm-status/activity.csv", "a")
activity.write(str(current_time) + "," + str(len(list_found_macs)))
activity.write("\n")
activity.close()
shutil.copyfile('/home/pi/msm-status/activity.csv', '/var/www/html/activity.csv')
 
 
 
#
#
#
####################
 
####################
#
#
#   Build Graph
#
 
 
plot_source = pd.read_csv("/home/pi/msm-status/activity.csv")
headers = ["time", "devicecount"]
plot_source_no_headers = pd.read_csv("/home/pi/msm-status/activity.csv", names = headers)
plot_source_no_headers.set_index("time", inplace= True)
plot_source_no_headers.plot()
plt.legend().set_visible(False)
plt.title("Heutige Aktivitäten")
plt.xlabel('Uhrzeit')
plt.ylabel('Aktive Geräte')
plt.savefig('/var/www/html/graph.png')
#
#
#
#
#
#
#####################
 
 
 
active_devices = len(list_found_macs)
 
dev_condition = ""
 
if active_devices == last_stat:
    dev_condition = "-"
elif active_devices > last_stat:
    dev_condition = "/"
elif active_devices < last_stat:
    dev_condition = "\\"
else:
    print("Kaputt")
 
html = open("/var/www/html/index.html", "w")
html_str_top = """
<!DOCTYPE html>
<html lang="de">
 <head>
   <meta charset="utf-8" />
   <meta name="viewport" content="width=device-width, initial-scale=1.0" />
   <title>Titel</title>
 </head>
 <body>
"""
html_str_bottom = """
 </body>
</html>
"""
html.write(html_str_top)
html.write("last_server_status_pull: " + str(current_time) + " " + str(date)  + '\n')
html.write("<br>" + '\n')
html.write("updates_every: 10 minutes" + '\n')
html.write("<br>" + '\n')
html.write("active_devices: " + str(len(list_found_macs)) + '\n')
html.write("<br>" + '\n')
html.write("trending: " + str(dev_condition))
html.write("<br>" + '\n')
html.write('<img src="graph.png"')
html.write(html_str_bottom)
html.close()
 
## Write status
 
status = open("/home/pi/msm-status/last_status.txt", "w")
status.write(str(len(list_found_macs)))
status.close()
 
last_date = open("/home/pi/msm-status/date.txt", "w")
last_date.write(str(date))
last_date.close()
