import meshtastic
from pubsub import pub
import datetime
import time
import json


# def onReceive(packet, interface):  # called when a packet arrives
#     print(f"Received: {packet}")


# # called when we (re)connect to the radio
# def onConnection(interface, topic=pub.AUTO_TOPIC):
#     # defaults to broadcast, specify a destination ID if you wish
#     interface.sendText("hello mesh")


# pub.subscribe(onReceive, "meshtastic.receive")
# pub.subscribe(onConnection, "meshtastic.connection.established")
# # By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
# interface = meshtastic.SerialInterface()

# bob = "Stop"

# interface.connect()

# # for n in range(1,10):
# #     time.sleep(10)
# #     interface.sendText(f"{n:2} | The current time is: {datetime.datetime.now()}")
    

# interface.sendText(f"Console complete. Self destruct engaged.")
# interface.close()

import meshtastic
from pubsub import pub


def onReceive(packet, interface):  # called when a packet arrives
    print(f"\nReceived: {json.dumps(packet, indent=2)}")
    #todo add write to file or SQS here
    
    bob = "STOP"


# called when we (re)connect to the radio
def onConnection(interface, topic=pub.AUTO_TOPIC):
    # defaults to broadcast, specify a destination ID if you wish
    interface.sendText("hello mesh")
    # interface.sendText("Lily Go Go, Check for receipt.",
    #                    destinationId='2988739000')


pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastic.connection.established")
# By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
interface = meshtastic.SerialInterface()
# interface.setOwner(long_name = "Master Control Program", short_name="MCP")
interface.setOwner("Master Control Program")

# print(f"--------- End of script! ---------")

