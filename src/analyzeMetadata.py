import json
import os

def loadObjectData(input_path):

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No object data file found at {input_path}")
    
    with open(input_path, 'r') as f:
        objects_dict = json.load(f)

    return objects_dict


def summarizeMetadataChanges(objectsDict):
    """Summarize metadata changes over time for each object."""
    summary = {}
    
    for obj_name, blocks in objectsDict.items():
        changes = {
            "total_blocks": len(blocks),
            "time_range": None,
            "position_changes": [],
            "z_changes": False,
            "width_changes": False
        }
        
        if blocks:
            # Calculate time range
            start_time = blocks[0]['rtime']
            end_time = blocks[-1]['rtime']
            changes["time_range"] = (start_time, end_time)
            
            # Track position changes
            prev_position = None
            prev_width = None
            for block in blocks:
                current_position = (block['x'], block['y'], block['z'])
                current_width = block.get('width', None)
                
                if prev_position and current_position != prev_position:
                    changes["position_changes"].append({
                        "time": block['rtime'],
                        "from": prev_position,
                        "to": current_position
                    })
                
                if prev_width is not None and current_width != prev_width:
                    changes["width_changes"] = True
                
                prev_position = current_position
                prev_width = current_width
            
            # Check if Z-coordinate changes
            z_values = {block['z'] for block in blocks}
            changes["z_changes"] = len(z_values) > 1
        
        summary[obj_name] = changes
    
    return summary


def printSummary(currentObjectDataPath = "../data/currentObjectData.json", togglePositionChanges=False):
    objectDict = loadObjectData(currentObjectDataPath)
    summary = summarizeMetadataChanges(objectDict)
    """Summarize metadata changes. second arg toggles detailed position changes"""
    print(f"\nFound {len(objectDict)} audio objects:")
    # for obj_name, blocks in objectDict.items():
    #     print(f"  - {obj_name}: {len(blocks)} position blocks")
    for obj_name, changes in summary.items():
        print(f"\nObject: {obj_name}")
        print(f"  Total Blocks: {changes['total_blocks']}")
        print(f"  Time Range: {changes['time_range']}")
        print(f"  Z-Coordinate Changes: {'Yes' if changes['z_changes'] else 'No'}")
        print(f"  Width Changes: {'Yes' if changes['width_changes'] else 'No'}")
        if togglePositionChanges and changes["position_changes"]:
            print(f"  Position Changes:")
            for change in changes["position_changes"]:
                print(f"    - At {change['time']}: {change['from']} -> {change['to']}")


