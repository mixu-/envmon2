

import xmltodict
import json
import math
import httplib, urllib

def insert_data(params):
    params = urllib.urlencode(params)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection("192.168.0.103")
    conn.request("POST", "/envmon2/chart/insert", params, headers)
    response = conn.getresponse()
    print response.status, response.reason
    data = response.read()
    print data
    conn.close()

with open("env.xml") as fd:
    doc = xmltodict.parse(fd.read())
    json_dump = json.dumps(doc)

for entry in doc["database"]["entry"]:
    timestamp = int(entry["time"]) * 1000
    temp = round(float(entry["temperature"]), 2)
    hum = round(float(entry["humidity"]), 2)
    if math.isnan(hum):
        hum = None
    if math.isnan(temp):
        temp = None

    print str(timestamp) + " / " + str(temp) + " / " + str(hum)
    insert_data({"datetime": timestamp, "bedroom_temperature": temp,
                 "bedroom_humidity": hum})
    break
