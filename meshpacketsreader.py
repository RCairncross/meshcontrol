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

def postprocessfiles(packetsfilename:str)->str:

    tsfmtstr = f"%Y%m%d_%H%M%S%f"
    nowobj = datetime.datetime.now()
    ts = nowobj.strftime(tsfmtstr)
    # ts = meshrecorder.timestamp

    outdir = os.path.split(packetsfilename)[0]
    out_packet = os.path.join(outdir, ts + '_postprocess_packets.txt')
    out_msg = os.path.join(outdir, ts + '_postprocess_messages.txt')
    out_pos=os.path.join(outdir, ts + '_postprocess_position.txt')
    out_user = os.path.join(outdir, ts + '_postprocess_user.json')

    #Read in all the packets form the raw file
    #Note, this assumes they are dictionaries
    # written out as one line per packet
    with open(packetsfilename, "r") as fp:
        linedict = fp.readlines()

    #Sort each line and write it to a file
    for l in linedict:

        packet_dict = json.loads(l)

        meshrecorder.sortandlog(packet=packet_dict,
                                packetsfname=out_packet,
                                msgfname=out_msg,
                                userfname=out_user,
                                posfname=out_pos,
                                unqiuelog=False)

    #open the files created and make them into actual compliant files
    out_packet = makejson(infile=out_packet, deleteinput=False)
    out_msg = makejson(infile=out_msg, deleteinput=False)
    # out_user = makejson(infile= out_user)
    out_pos = makegeojson(infile=out_pos)
    

if __name__=='__main__':
    

    #All the packets received during a session
    infile = r'C:\projects\Dropbox\code\meshcontrol\logs\20201124_192950010877_packets.json'

    #Work through the file of packets and parse them out
    postprocessfiles(packetsfilename=infile)
    

    print("==== Thats All Folks ====")
