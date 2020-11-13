import meshtastic
from pubsub import pub
import datetime
import time
import csv
import json

# # csvfile = open(csv_file, 'w')
# writer = csv.DictWriter('data.csv')

msgfilename = 'messages.json'
csvfilename = 'data.csv'
template = {
            'from': "",
            'to': "",
            'type': "",
            'message': "",
            "hopLimit": ""
            }
    
# with open(csvfilename, 'w+') as f:
#     w = csv.DictWriter(f, template.keys())
#     w.writeheader()



msg_counter = 0
prevkeys = {}

def onReceive(packet, interface):  # called when a packet arrives
    # print(f"Received: \n{json.dumps(packet, indent=2)}")
    print(f"Received Raw: \n{json.dumps(packet, indent=2)}\n")
    #todo add write to file or SQS here
    with open('packets.txt', 'a') as fp:
        fp.write(json.dumps(packet)+'\n')
    
    if 'data' in packet['decoded'].keys():
        
        # Pop out the text of the message and add it back into 
        #   the packet and publish it as a JSON in a the file    
        msg = packet.pop('decoded').pop('data').pop('text')
        packet['message'] = msg
        with open(msgfilename, 'a') as fp:
            fp.write(json.dumps(packet)+'\n')
            

    elif 'user' in packet['decoded'].keys():
        print("This is a user packet")
                
    else:
        print('This is an undefined packet')


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


pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastic.connection.established")

# By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
interface = meshtastic.SerialInterface(connectNow=False)
interface.setOwner("Master Control Program",
                   short_name='MCP')
interface.connect()
# interface.sendText(f"The current time is: {datetime.datetime.now()}")


print(f"--------- End of script! ---------")

