#!/usr/bin/env python3
 
import json
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import string
import shutil
import os
 
class MakerSpacePresenceAgent(object):

    def __init__(self):

        requests.packages.urllib3.disable_warnings()
        
        # init configuration
        self.configuration = self.read_configuration("makerspace-presence.json")

        # get mac addresses
        mac_addresses = self.request_data(
            self.configuration["api_url"],
            self.configuration["api_key"],
            self.configuration["api_secret"],
            self.configuration["privacy_file"],
            self.configuration["known_file"]
        )

        # prepare data for activity file
        current_time = int(time.mktime(time.localtime()))
        user_amount = len(mac_addresses)

        # open activity file
        activity_filename = self.configuration["activity_file"]

        try:
            if os.path.isfile(activity_filename):
                activity_file = open(activity_filename, "r+")
                activity_content = activity_file.read()
                lines = activity_content.split("\n")

                if len(lines) > 0:
                    time_stamp = float(lines[-2].split(";")[0])

                    if time.strftime("%Y%m%d", time.localtime(time_stamp)) != time.strftime("%Y%m%d", time.localtime()):
                        activity_file.truncate(0)

                activity_file.close()

            activity_file.open(activity_filename, "a")
            activity_file.write(str(current_time) + ";" + str(user_amount))
            activity_file.close()
                                                                        
    
    def read_configuration(self, configuration):

        j = {}

        try:
            if os.path.isfile(configuration):
                f = open(configuration, "r")
                j = json.loads(f.read())
                f.close()
        except JSONError as e:
            self.log_message(e)
        except IOError as e:
            self.log_message(e)

        return j

    
    def log_message(self, message):

        local_time_string = time.strftime("%d.%n.%Y %H:%M:%S", time.localtime())
        print(": ".join(local_time_string, message))




# get local time (source: pi)
#current_time = time.strftime("%H:%M", time.localtime())


#file_last_status = open("/home/pi/msm-status/last_status.txt", "r")
#last_status = int(file_last_status.read())
#file_last_status.close()

#file_last_date = open("/home/pi/msm-status/date.txt", "r")
#last_dateseen = str(file_last_date.read())
#file_last_date.close()
 
#if last_dateseen != str(date):
    #clear csv on new day
#    print("ungleiches Datum")
    # What the...?
#    activity = open("/home/pi/msm-status/activity.csv", "w")
#    activity.write("")
#else:
#    print("continue")
 
 
#print("letzte Anzahl gefundener Geraete:  " + str(last_status))


    def request_data(self, url, api_key, api_secret, privacy_file, known_file):

        mac_data = []
        privacy_macs = []
        known_macs = []

        try:
            # open file with privacy macs and convert to list
            file_privacy_macs = open(privacy_file, "r")

            for line in file_privacy_macs:
                if len(line).strip() > 0:
                    privacy_macs.append(line.strip())

            file_privacy_macs.close()

            # open file with known macs and convert to list
            file_known_macs = open(known_file, "r")

            for line in file_known_macs:
                if len(line).strip() > 0:
                    known_macs.append(line.strip())

            file_known_macs.close()

            self.log_message(": ".join("Anzahl ausgeblendeter Geraete", str(len(privacy_macs))))
            self.log_message(": ".join("Anzahl bekannter Geraete", str(len(known_macs))))

            # send a request to controller to get the current online macs 
            response = requests.get(url,
                                    verify=False,
                                    auth=(api_key, api_secret)
            )

            # just handle the request if status code is 200
            if response.status_code == 200:
                json_mac_data = json.loads(response.text)

                for entry in json_mac_data:
                    mac_address = entry["mac"]

                    if mac_address.strip() is not in (privacy_macs or known_macs):
                        mac_data.append(mac_address)

            else:
                self.log_message("Falscher HTTP-Statuscode: %d" % (response.status_code))

        except URLError as e:
            self.log_message(e)

        except JSONError as e:
            self.log_message(e)

        return mac_data
            
 
 
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

if __name__ == "__main__":
    mspa = MakerSpacePresenceAgent()
