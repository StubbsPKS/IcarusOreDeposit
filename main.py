# -*- coding: utf-8 -*-
"""
Created on Tue Nov  4 20:40:42 2025

@author: maiev
"""

import zlib
import base64
import struct

def process_prospect_file(file_bytes: bytes):
    """
    Processes a dropped Prospect JSON file.
    Expects bytes from JS FileReader.
    Returns decompressed blob as bytes.
    """
    
    
    if isinstance(file_bytes, memoryview):
        file_bytes = file_bytes.tobytes()

    text = file_bytes.decode("utf-8").splitlines()
    text = file_bytes.decode("utf-8");
    text = text.splitlines(keepends=True);
    blob = None
    for line in text:
        if "BinaryBlob" in line:
            blob = line
            break

    if not blob:
        raise ValueError("No BinaryBlob found in file")
    # Strip leading/trailing characters
    blobf = blob[17:-2]
    decoded_bytes = base64.b64decode(blobf)   
    data = zlib.decompress(decoded_bytes)
    
    world = [];
    map_scale = 0;
    
    if data.find(b'Terrain_016',0,len(data)) !=-1 :
        world = "Olympus";
        map_scale = 4096;
    elif data.find(b'Terrain_017',0,len(data)) !=-1 :
        world = "Styx";
        map_scale = 4096;
    elif data.find(b'Terrain_019',0,len(data)) !=-1 :
        world = "Prometheus";
        map_scale = 2048;
    else :
        world = "Unknown";   
    
    Max_map_size_meters = 403200;
    Min_map_size_meters = -403200;
    
    scale = (Max_map_size_meters-Min_map_size_meters)/map_scale;
    
    Coords = [[], [], []];
    Ressource = [];
    offset = 0;
    count = 0;
    while offset!=-1:
      offset = data.find(b'Script/Icarus.ResourceDepositRecorderComponent',offset,len(data))
      if(offset!=-1):
          offset = data.find(b'NameProperty',offset,len(data))
          offset+=13;
          struct_size = int.from_bytes(data[offset:offset+8], 'little')
          offset +=8+1;
          name_len = int.from_bytes(data[offset:offset+4], 'little')
          offset+=4;
          element_name = data[offset:offset+name_len-1].decode('utf-8', errors='ignore');
          offset = data.find(b'Vector',offset,len(data))
          offset +=7 + 1;
          offset+=16
          Vector = data[offset:offset+12];
          x, y, z = struct.unpack('<fff', Vector)
          Coords[0].append(x);
          Coords[1].append(y);
          Coords[2].append(z); 
          Ressource.append(element_name);
          count+=1;
    
    Shifted_X = [(x - Min_map_size_meters)/scale for x in Coords[0]];
    Shifted_Y = [map_scale - (Max_map_size_meters - y)/scale for y in Coords[1]]
    return world, Shifted_X, Shifted_Y, Ressource

# if __name__ == "__main__":
#     with open("Styx Hard Quest.json", "rb") as f:
#         data = f.read()
#     result = process_prospect_file(data)
    
