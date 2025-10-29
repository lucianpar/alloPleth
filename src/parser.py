import json
from lxml import etree
import os

# heavy usage of claude sonnet (in copilot) for dealing with ebu formatting 

'''on EBU:
Namespace: Uses "urn:ebu:metadata-schema:ebuCore_2016" - the 2016 version of EBU's metadata schema

The parser looks for audioChannelFormat elements with typeDefinition="Objects" - these represent individual audio stems or elements that can move in 3D spac

- Position Blocks: Each object has multiple audioBlockFormat elements that define its position over time:

- rtime: Relative start time (e.g., "00:03:09.59419")
duration: How long this position lasts
position elements with coordinates X, Y, Z

- Spatial Metadata: Additional properties like:

- cartesian: Whether coordinates are Cartesian (1) or spherical (0)
width, depth, height: Object size/spread in space
diffuse: How spread out the sound is

'''

def extractObjectPositions(xml_path):
    """extract positions from XML ADM metadata in EBU format.

        returns dict mapping object names to lists of position blocks
        Each  block is a dict with: 'rtime', 'duration', 'x', 'y', 'z'
    """
    # Updated namespace for ebuCore_2016
    ns = {"ebu": "urn:ebu:metadata-schema:ebuCore_2016"}
    tree = etree.parse(xml_path)
    
    objects = {}
    
    # Find all audioChannelFormat elements with typeDefinition="Objects"
    for channel in tree.xpath("//ebu:audioChannelFormat[@typeDefinition='Objects']", namespaces=ns):
        name = channel.attrib.get("audioChannelFormatName", "Unnamed")
        
        # Get all audioBlockFormat elements for this channel
        blocks = []
        for block in channel.xpath(".//ebu:audioBlockFormat", namespaces=ns):
            # Extract time information
            rtime = block.attrib.get("rtime", "00:00:00.00000")
            duration = block.attrib.get("duration", "00:00:00.00000")
            
            # Extract position coordinates
            position_data = {
                'rtime': rtime,
                'duration': duration,
                'x': 0.0,
                'y': 0.0,
                'z': 0.0
            }
            
            # Get position elements
            for pos in block.xpath(".//ebu:position", namespaces=ns):
                coord = pos.attrib.get("coordinate", "")
                value = float(pos.text) if pos.text else 0.0
                
                if coord == "X":
                    position_data['x'] = value
                elif coord == "Y":
                    position_data['y'] = value
                elif coord == "Z":
                    position_data['z'] = value
            
            # Extract additional metadata if present
            cartesian = block.find(".//ebu:cartesian", namespaces=ns)
            if cartesian is not None:
                position_data['cartesian'] = int(cartesian.text) if cartesian.text else 1
            
            width = block.find(".//ebu:width", namespaces=ns)
            if width is not None:
                position_data['width'] = float(width.text) if width.text else None
                
            depth = block.find(".//ebu:depth", namespaces=ns)
            if depth is not None:
                position_data['depth'] = float(depth.text) if depth.text else None
                
            height = block.find(".//ebu:height", namespaces=ns)
            if height is not None:
                position_data['height'] = float(height.text) if height.text else None
            
            blocks.append(position_data)
        
        if blocks:
            objects[name] = blocks
    
    return objects

def saveObjectData(objectsDict, outputPath="../data/currentObjectData.json"):
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)

    with open(outputPath, 'w') as f:
        json.dump(objectsDict, f, indent=2)

    print(f"Saved object data to {outputPath}")

def loadObjectData(inputPath="../data/currentObjectData.json"):
    if not os.path.exists(inputPath):
        raise FileNotFoundError(f"No object data file found at {inputPath}")

    with open(inputPath, 'r') as f:
        objectsDict = json.load(f)

    print(f"Loaded object data from {inputPath}")
    return objectsDict



def parseTimecodeToSeconds(timecode):
    """Convert timecode string (HH:MM:SS.SSSSS) to seconds."""
    hours, minutes, seconds = timecode.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def getPositionAtTime(blocks, time_seconds):
    """
    returns dict of Position data at the specified time, or None if not found
    """
    for block in blocks:
        start_time = parseTimecodeToSeconds(block['rtime'])
        duration = parseTimecodeToSeconds(block['duration'])
        end_time = start_time + duration
        
        if start_time <= time_seconds < end_time:
            return block
    
    return None


def parseMetadata(xmlPath, ToggleExportJSON = True, TogglePrintSummary = True):
    """CALLS OTHER FUNCTIONS - parses metadata from XML file, optionally exports to JSON and prints summary"""
    objectsDict = extractObjectPositions(xmlPath)

    if ToggleExportJSON:
        saveObjectData(objectsDict, outputPath="../data/currentObjectData.json")

    if TogglePrintSummary:
        from src.analyzeMetadata import printSummary
        printSummary(currentObjectDataPath="../data/currentObjectData.json", togglePositionChanges=False)

    return objectsDict