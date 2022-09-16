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
RELEVANCE_THRESHHOLD = 2 # maximum fov
RELEVANCE_THRESHHOLD_ZOOM_OUT = 30
MIN_FOV_DECREMENT = 0.8# minimum zoom-in speed (in degrees / seconds)
MAX_FOV_DECREMENT = 2
MEASURE_DISTANCE = 10 # sample points in a single measurement (in seconds) larger values reduce influence of measuring errors at the cost of detail loss
MIN_DISTANCE = 5 # minimum time between highlights (in seconds)
#AZIMUTH = "sensorRelativeAzimuth"
#ELEVATION = "sensorRelativeElevation"
#MIN_AZIMUTH = 7
#MIN_ELEVATOR = 2 

CHANGE = "change"
#----------------------------getOpts--------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("-r", help="\nZoomed areas must have a zoom-value greater than a spefifc value.")
parser.add_argument('-v', help="\nOnly zomm areas are displayed for which a specified zoom-in speed has been observed." )
parser.add_argument('-d', help="\nTime window for one measurement.")
parser.add_argument('-t', help="\nZoomed areas that are less than 5 seconds apart are combined into one zoom.")
args = parser.parse_args()
if args.r:
    RELEVANCE_THRESHHOLD = input("Value for the Relevance Threshhold: " + args.r)
elif args.v:
    x = input("Value for the Min_FOV_Decrement: " + args.v)
    MIN_FOV_DECREMENT = int(args.v)
elif args.d:
    MEASURE_DISTANCE = input("Value for the Measure Distance: " + args.d)
elif args.t:
    MIN_DISTANCE = input("Value for the Min Distance: " + args.t)


# ------------------------- Load file --------------------------
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
    #stamp[AZIMUTH] = float(stamp[AZIMUTH])
    #stamp[ELEVATION] = float(stamp[ELEVATION])
    
# ------------------- Calculate differential -------------------
measure_index = -MEASURE_DISTANCE
TIMESTAMPS = [{ TIME: DATA[0][TIME], ZOOM: DATA[0][ZOOM], CHANGE: 0 }]

for stamp in DATA[1:]:
    if(measure_index < 0):
        diff = 0
    else:
        # Calculation of rate of change
        
        diff = stamp[ZOOM] / DATA[measure_index][ZOOM]
        #focus_A = abs(stamp[AZIMUTH] - DATA[measure_index][AZIMUTH])
        #focus_B = abs(stamp[ELEVATION] - DATA[measure_index][ELEVATION])
    data_stamp = { TIME: stamp[TIME], ZOOM: stamp[ZOOM], CHANGE: diff }
    TIMESTAMPS.append(data_stamp)
    measure_index += 1



# ---------------------- Search highlights for Zoom-in----------------------
HIGHLIGHTS_ZOOM_IN = []
last_highlight = datetime(1, 1, 1)

for stamp in TIMESTAMPS:
    # Conditions
    time = (stamp[TIME] - last_highlight).total_seconds() < MIN_DISTANCE
    zoom = stamp[ZOOM] > RELEVANCE_THRESHHOLD
    diff = stamp[CHANGE] > -MIN_FOV_DECREMENT

    if(time and zoom or diff):
        continue

    HIGHLIGHTS_ZOOM_IN.append(stamp)
    last_highlight = stamp[TIME]
#-------------------Search highlights for Zoom-out-----------------------------
HIGHLIGHTS_ZOOM_OUT = []
last_highlight = datetime(1,1,1)

for stamp in TIMESTAMPS:
    #Conditions
    time = (stamp[TIME] - last_highlight).total_seconds() < MIN_DISTANCE
    zoom = stamp[ZOOM] < RELEVANCE_THRESHHOLD_ZOOM_OUT
    change = stamp[CHANGE] > MIN_FOV_DECREMENT

    if(time and change):
        continue

    HIGHLIGHTS_ZOOM_OUT.append(stamp)
    last_highlight = stamp[TIME]
#-------------------Search highlights for Change of camera focus---------------------
#HIGHLIGHTS_FOCUS = []
#last_highlight = datetime(1,1,1)
#for stamp in TIMESTAMPS:
    # Conditions
 #   time = (stamp[TIME] - last_highlight).total_seconds() < MIN_DISTANCE
  #  focus_A = True
   # focus_B = True

    #if(time and focus_A or focus_B):
        #continue
    #HIGHLIGHTS_FOCUS.append(stamp)
    #last_highlight = stamp[TIME]

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

#----------------------------------------------------------------------------------------------------------
   # print("\n\nHighlights for Change of camera focus", file=external_file)
    #print("_______________________________________________", file=external_file)
    #print("\nTimestamp\t\told coordinates\tnew coordinates", file=external_file)
    #for stamp in HIGHLIGHTS_FOCUS:
     #   time = str(stamp[TIME])

    #print("\n" + str(len(HIGHLIGHTS_FOCUS)) + " highlights were found.\n", file=external_file)   

external_file.close()