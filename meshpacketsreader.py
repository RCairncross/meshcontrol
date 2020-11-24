import datetime
import geojson
import json
import os

import meshrecorder


def makejson(infile:str, outext:str='.json', deleteinput: bool= True)-> str:
    
    #init
    outarray = []
    
    #create the output file name
    outfile = os.path.splitext(infile)[0]+outext
    
    #load in the file to memory
    with open(infile, "r") as infp:
        linedict = infp.readlines()
        
    #convert the string lines into dictionaries
    for l in linedict:
        outarray.append(json.loads(l))
        
    #write out the output
    if os.path.exists(outfile):
        os.remove(outfile)
        
    with open(outfile, "w") as outfp:
        json.dump(outarray,outfp)
        
    #Delete the input file if so desired
    if deleteinput and os.path.exists(infile):
        os.remove(infile)
    
    return outfile


def makegeojson(infile: str, outext: str = '.geojson', deleteinput: bool = True) -> str:

    #init
    geofeatures = []

    #create the output file name
    outfile = os.path.splitext(infile)[0]+outext

    #load in the file to memory
    with open(infile, "r") as infp:
        linedict = infp.readlines()

    for c, l in enumerate(linedict):
        l = json.loads(l)
        geofeatures.append(geojson.Feature(id=c+1,
                                           geometry=l['geometry'],
                                           properties=l['properties']))

    #write out the output
    if os.path.exists(outfile):
        os.remove(outfile)

    with open(outfile, "w") as outfp:
        geojson.dump(geojson.FeatureCollection(geofeatures), outfp)

    #Delete the input file if so desired
    if deleteinput and os.path.exists(infile):
        os.remove(infile)

    return outfile

if __name__=='__main__':
    

    
    # infile = '20201118_packets.json'
    infile = 'packets.txt'

    tsfmtstr = f"%Y%m%d_%H%M%S%f"
    nowobj = datetime.datetime.now()
    ts = nowobj.strftime(tsfmtstr)
    # ts = meshrecorder.timestamp

    out_packet = ts + '_packets.txt'
    out_msg = ts + '_messages.txt'
    out_pos = ts + '_position.txt'
    out_user = ts + '_user.json'

    #Read in all the packets form the raw file
    #Note, this assumes they are dictionaries 
    # written out as one line per packet
    with open(infile, "r") as fp:
        linedict = fp.readlines()

    #Sort each line and write it to a file
    for l in linedict:
        
        packet_dict = json.loads(l)
        
        meshrecorder.sortandlog(packet=packet_dict,
                                packetsfname= out_packet,
                                msgfname= out_msg,
                                userfname= out_user,
                                posfname= out_pos)        

    #open the files created and make them into actual compliant files
    out_packet = makejson(infile=out_packet)
    out_msg = makejson(infile= out_msg)
    # out_user = makejson(infile= out_user)
    
    out_pos = makegeojson(infile= out_pos)        

    print("==== Thats All Folks ====")
