import meshtastic
from pubsub import pub
import datetime
import time
import logging
import json
import geojson
import os


Version = '0.1.0.5'
Source = os.path.abspath(__file__)
__version__ = Version
__author__ = "Gabe Ladd - Advanced Concepts Consulting"
# __name__ = os.path.splitext(os.path.split(Source)[1])[0]


# # csvfile = open(csv_file, 'w')
# writer = csv.DictWriter('data.csv')

# msgfilename = 'messages.json'
# csvfilename = 'data.csv'
# packetsname = 'packets.txt'
runtimestemp = ""
template = {
            'from': "",
            'to': "",
            'type': "",
            'message': "",
            "hopLimit": ""
            }
    


msg_counter = 0
prevkeys = {}


# ____________________________________________________________________________________
# Setup Log files

"""
Level Options:
logging.DEBUG
logging.INFO
logging.WARNING
logging.ERROR
logging.CRITICAL
"""
logfile_dir = '' #set to '' to log in current working dir
logfile_name = 'MeshRecorder.log'
logger_name = 'Recorder'
loglevel = logging.DEBUG
fmt_str = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'

# log file
if logfile_dir != '' and os.path.isdir(logfile_dir):
    logfilepath = os.path.join(logfile_dir, logfile_name)
else:
    logfilepath = os.path.join(os.getcwd(), logfile_name)

# ---- Setup Error logfile
error_logpath = os.path.join(os.path.split(logfilepath)[0],
                                os.path.splitext(os.path.split(logfilepath)[1])[0] + '_errors' +
                                os.path.splitext(os.path.split(logfilepath)[1])[1])

# ---- Setup the Log Objects
formatter = logging.Formatter(fmt_str)

# Check for duplicate loggers
log = logging.getLogger(logger_name)

if not log.handlers:
    log.setLevel(loglevel)

    # first handle - Streaming to the console
    consolhandle = logging.StreamHandler()
    consolhandle.setFormatter(formatter)
    consolhandle.setLevel(loglevel)
    log.addHandler(consolhandle)

    # second handle - for full log file
    loghandle = logging.FileHandler(logfilepath, mode='w')
    loghandle.setFormatter(formatter)
    loghandle.setLevel(loglevel)
    log.addHandler(loghandle)

    # error handle - for error log file
    errorhandle = logging.FileHandler(error_logpath, mode='w')
    errorhandle.setFormatter(formatter)
    errorhandle.setLevel(logging.ERROR)
    log.addHandler(errorhandle)

log.info('---- Start of Log ----')
log.info('Logging to: %s' % (logfilepath))
log.info('----------------------')
log.info(' Log Version: %s' % Version)
log.info(' Source: %s' % os.path.abspath(__file__))
log.info('----------------------')
log.debug(' Test Debug Level')
log.info(' Test Info Level')
log.warning(' Test Warning Level - You have been warned')
log.info('----------------------')

# ____________________________________________________________________________________



# def features2geojson(filepath, feature_array):
#     """Writes a feature array to a file as a feature collection

#     Returns:
#         [str]: File path input to write data to.
#     """

#     #Write out the data
#     with open(filepath, 'w') as f:
#         geojson.dump(geojson.FeatureCollection(feature_array), f)

#     return filepath

def getpt(pkt: dict, latstr: str = 'latitude', lonstr: str = 'longitude', altstr: str = 'height', prefix: str = ''):
    """Walk through the keys of a dictionary and extract the 3 keys need to make a spatial point and return a point.
    
    This function loops through the keys of a dictionary and identifies the x,y,z entries by string match with the key value. 
    Prefix options can be used if there are more than one entires in the dictionary that have the search strings in them. 
    The code assumes the prefix is sparated by a period character.
    
    Returns:
        [Point]: 3D point in space. If one value can not be found in the dictionary key that value is set to zero.
    """

    #Initialize the spatial variables with zero values
    lat = 0.0
    lon = 0.0
    alt = 0.0

    #If the prefix is included append it to the search strings
    if prefix != '':
        latstr = prefix+'.'+latstr
        lonstr = prefix+'.'+lonstr
        altstr = prefix+'.'+altstr

    #Sort through all the keys in the dictionary for the ones
    # wer are interseted in and convert the value into a floating
    # point number
    for key in pkt:
        if pkt[key] == '':
            pass
        elif latstr in key:
           lat = float(pkt[key])
        elif lonstr in key:
            lon = float(pkt[key])

        elif altstr in key:
            alt = float(pkt[key])

    #Compbine the new float values into a GeoJson Point
    pt = geojson.Point((lon,
                        lat,
                        alt))

    return pt

def timestamp(fmtstr: str = f"%Y-%m-%dT%H:%M:%S.%f"):
    tobj = time.now()
    return tobj.strftime(fmtstr)

def sortandlog(packet:dict, 
               packetsfname:str = 'packets.json',
               msgfname: str = 'messages.json',
               userfname: str = 'user.json',
               posfname: str = 'position.json'):
    
    #init
    hasalt = False
    
    log.debug(f"Received Raw: \n{json.dumps(packet, indent=2)}\n")
    #todo add write to file or SQS here
    with open(packetsfname, 'a') as fp:
        fp.write(json.dumps(packet)+'\n')

    if 'data' in packet['decoded'].keys():

        # Pop out the text of the message and add it back into
        #   the packet and publish it as a JSON in a the file
        msg = packet.pop('decoded').pop('data').pop('text')
        packet['message'] = msg
        with open(msgfname, 'a') as fp:
            fp.write(json.dumps(packet)+'\n')

    elif 'user' in packet['decoded'].keys():
        log.debug("This is a user packet")
        
    elif "position" in packet['decoded'].keys():
        # Pop out the text of the message and add it back into
        #   the packet and publish it as a JSON in a the file
        if "latitude" in packet['decoded']['position'].keys() and "longitude" in packet['decoded']['position'].keys():
            #extract the postition data from the packet
            pos = packet.pop('decoded').pop("position")
        
            # if hasalt:
            #create a geojoson pt
            pt = getpt(pkt=pos,
                    latstr="latitude",
                    lonstr="longitude",
                    altstr="altitude"
                    )

            # else:
            #     #create a geojoson pt
            #     pt = getpt(pkt=pos,
            #                latstr="latitude",
            #                lonstr="longitude"
            #                )
            """ Example from test file
            "position": {
                    "altitude": -21,
                    "batteryLevel": 58,
                    "latitudeI": 279490758,
                    "longitudeI": -827657774,
                    "time": 316311464,
                    "latitude": 27.9490758,
                    "longitude": -82.76577739999999
            """
            #add the decoded data into the packet to be used as attribute data
            try:
                packet["altitude"] = pos.pop("altitude")
                hasalt = True
            except:
                print("Packet has no altitude data")
                
            try:
                packet["batteryLevel"] = pos.pop("batteryLevel")
            except:
                print("Packet has no battery level data")
    
            try:
                packet["time"] = pos.pop("time")
            except:
                print("Packet has no time data")
    
            #The packet has to have these parameters
            packet["latitude"] = pos.pop("latitude")
            packet["longitude"] = pos.pop("longitude")
        
                           
            
            # combine into a gejson message to be written
            feature = geojson.Feature(geometry=pt, properties=packet)
                

            with open(posfname, 'a') as fp:
                # fp.write(json.dumps(packet)+'\n')
                # geojson.dump(geojson.FeatureCollection(feature), fp)
                # geojson.dump(geojson.Feature(geometry=pt, properties=packet),fp=fp)
                fp.write(str(geojson.Feature(geometry=pt, properties=packet))+'\n')
        
        else:
            print(f"Postition packet is incomplete not writting to file:\n{json.dumps(packet)}\n\n")

    else:
        print('This is an undefined packet')
    
    

def onReceive(packet, interface):  # called when a packet arrives
    # print(f"Received: \n{json.dumps(packet, indent=2)}")
    packet['loggedtime']=timestamp()
    sortandlog(packet= packet)


# called when we (re)connect to the radio
def onConnection(interface, topic=pub.AUTO_TOPIC):
    # defaults to broadcast, specify a destination ID if you wish
    # interface.sendText("hello mesh")
    now = datetime.datetime.now()
    nowstr = now.strftime("%m/%d/%Y, %H:%M:%S")
    
    # interface.sendText(f"{nowstr}|Connecting to mesh!")
    interface.sendText(nowstr+"|Connecting to mesh!")
    # interface.sendText("Lily Go Go, Check for receipt.",
    #                    destinationId='2988739000')
    # interface.sendText('Delivery Type Testing',
    #                    destinationId=2988739000)


if __name__ == "__main__":
    log.info("Starting Meshtasic recorder")
    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")

    # By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
    interface = meshtastic.SerialInterface(connectNow=False)
    interface.setOwner("Master Control Program",
                    short_name='MCP')
    interface.connect()
    # interface.sendText(f"The current time is: {datetime.datetime.now()}")


