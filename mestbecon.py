import meshtastic
import time
import datetime
# By default will try to find a meshtastic device, otherwise provide a device path like /dev/ttyUSB0
# interface = meshtastic.SerialInterface()
# or sendData to send binary data, see documentations for other options.
# interface.debugOut()


# interface = meshtastic.SerialInterface(connectNow=False)
# interface.setOwner("Big Beacon",
#                    short_name='BB')
# interface.connect()
# interface.sendText(text="Test message! Do you hear me????")


beaconcounter = 0
beaconcycles = 10
beaconinterval = 20


interface = meshtastic.SerialInterface()
time.sleep(1)
interface.sendText("Beacon is online")

while beaconcounter <= beaconcycles:
    #pause the cycle
    if beaconinterval>=60:
        print(f"Sleeping for {beaconinterval}")
    time.sleep(beaconinterval)
    
    #time stamp
    now = datetime.datetime.now()
    nowstr = now.strftime("%m/%d/%Y-%H:%M:%S")

    msg = f"{beaconcounter:05}|{nowstr}|Beacon Message."
    print(msg)
    interface.sendText(msg)
    interface.sendPosition()

    beaconcounter+=1

print("--- End of Script ---")
