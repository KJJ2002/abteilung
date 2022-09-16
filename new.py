import json
from datetime import datetime
from pickle import NONE

import argparse
from re import T
import sys


# --------------------------- CONFIG ---------------------------
JSON_FILE = "metadata.json" # file containing metadata
JSON_OBJECT = ""
TIME = "timestamp" # JSON name for time values
ZOOM = "sensorVerticalFOV" # JSON name for zoom values
MEASURE_DISTANCE = 10
MIN_DISTANCE = 5

CHANGE = "change"

FILE = open(JSON_FILE)
DATA = json.load(FILE)
FILE.close()

if JSON_OBJECT != "":
    DATA = DATA[JSON_OBJECT]
    
for stamp in DATA:
    time = stamp[TIME]
    year = int(time[0:4])
    month = int(time[5:7])
    day = int(time[8:10])
    hour = int(time[11:13])
    minute = int(time[14:16])
    second = int(time[17:19])
    stamp[TIME] = datetime(year, month, day, hour, minute, second)
    stamp[ZOOM] = float(stamp[ZOOM])
    
#---------------Measurement---------------------------------------
measure_index = -MEASURE_DISTANCE
TIMESTAMPS = [{ TIME: DATA[0][TIME], ZOOM: DATA[0][ZOOM], CHANGE: 0 }]

for stamp in DATA[1:]:
    if(measure_index < 0):
        diff = 0
    else:
        diff = stamp[ZOOM] / DATA[measure_index][ZOOM]
    data_stamp = { TIME: stamp[TIME], ZOOM: stamp[ZOOM], CHANGE: diff }
    TIMESTAMPS.append(data_stamp)
    measure_index += 1

HIGHLIGHTS_ZOOM_IN, HIGHLIGHTS_ZOOM_OUT= [], []
last_highlight = datetime(1, 1, 1)

for stamp in TIMESTAMPS:
    # Conditions
    time = (stamp[TIME] - last_highlight).total_seconds() < MIN_DISTANCE
    zoom_in = diff < 0.1
    zoom_out = diff > 2
     

    if(time and zoom_in):
        continue
    last_highlight = stamp[TIME]

    HIGHLIGHTS_ZOOM_IN.append(stamp)

    if(time and zoom_out):
        continue
    HIGHLIGHTS_ZOOM_OUT.append(stamp)
    last_highlight = stamp[TIME]

# ----------------------- Print results ------------------------
with open ('out.txt','w') as external_file:
    orig_stdout = sys.stdout
    external_file = open('out.txt','w')
    print("Highlights for Zoom-in", file=external_file)
    print("_______________________________________________", file=external_file)
    print("\nTimestamp\t\tVertical FOV\tRate of Change", file=external_file)
    print("------------------------------------------------------", file=external_file)

    for stamp in HIGHLIGHTS_ZOOM_IN:
        time = str(stamp[TIME])
        zoom = str("%.3f" % stamp[ZOOM]) + "°"
        change = str("%.3f" % stamp[CHANGE]) + "°/s"
        print("{:>9} {:>16} {:>17}".format(time, zoom, change), file=external_file)

    print("\n" + str(len(HIGHLIGHTS_ZOOM_IN)) + " highlights were found.\n", file=external_file)   
#-----------------------------------------------------------------------------------------------
    print("\n\n\nHighlights for Zoom-out", file=external_file)
    print("_______________________________________________", file=external_file)
    print("\nTimestamp\t\tVertical FOV\tRate of Change", file=external_file)
    print("------------------------------------------------------", file=external_file)

    for stamp in HIGHLIGHTS_ZOOM_OUT:
        time = str(stamp[TIME])
        zoom = str("%.3f" % stamp[ZOOM]) + "°"
        change = str("%.3f" % stamp[CHANGE]) + "°/s"
        print("{:>9} {:>16} {:>17}".format(time, zoom, change), file=external_file)

    print("\n" + str(len(HIGHLIGHTS_ZOOM_OUT)) + " highlights were found.\n", file=external_file)   