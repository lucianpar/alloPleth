import json
import os
import csv

def loadProcessedData(processed_dir="processedData"):
    """Load all JSON files from processedData directory.
    
    Returns:
        dict: Contains 'globalData', 'directSpeakerData', and 'objectData'
    """
    data = {}
    
    # Load global data
    global_path = os.path.join(processed_dir, "globalData.json")
    if os.path.exists(global_path):
        with open(global_path, 'r') as f:
            data['globalData'] = json.load(f)
        print(f"Loaded globalData from {global_path}")
    else:
        data['globalData'] = {}
        print(f"Warning: {global_path} not found")
    
    # Load direct speaker data
    speaker_path = os.path.join(processed_dir, "directSpeakerData.json")
    if os.path.exists(speaker_path):
        with open(speaker_path, 'r') as f:
            data['directSpeakerData'] = json.load(f)
        print(f"Loaded directSpeakerData from {speaker_path}")
    else:
        data['directSpeakerData'] = {}
        print(f"Warning: {speaker_path} not found")
    
    # Load object data
    object_path = os.path.join(processed_dir, "objectData.json")
    if os.path.exists(object_path):
        with open(object_path, 'r') as f:
            data['objectData'] = json.load(f)
        print(f"Loaded objectData from {object_path}")
    else:
        data['objectData'] = {}
        print(f"Warning: {object_path} not found")
    
    return data


def parseTimecodeToSeconds(timecode):
    """Convert timecode string (HH:MM:SS.SSSSS) to seconds."""
    try:
        hours, minutes, seconds = timecode.split(':')
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except:
        return 0.0


def createSpatialInstructionsCSV(processed_dir="processedData", output_path="forExport/spatialInstructions.csv"):
    """Create spatial instructions CSV with timestamped position data.
    
    CSV format: id,time,x,y,z,dynamic
    - id: object/speaker name
    - time: timestamp in seconds
    - x,y,z: cartesian coordinates
    - dynamic: True/False (True = moving object, False = static)
    
    Static channels (DirectSpeakers and non-moving objects) are placed first,
    followed by dynamic channels.
    
    Args:
        processed_dir (str): Directory containing processed JSON files
        output_path (str): Where to save the CSV file
    
    Returns:
        int: Number of rows written
    """
    # Load all processed data
    data = loadProcessedData(processed_dir)
    
    static_rows = []
    dynamic_rows = []
    static_count = 0
    dynamic_count = 0
    
    # Process DirectSpeakers as static objects (time = 0.00)
    for speaker_name, speaker_info in data.get('directSpeakerData', {}).items():
        row = {
            'id': speaker_name,
            'time': 0.00,
            'x': speaker_info.get('x', 0.0),
            'y': speaker_info.get('y', 0.0),
            'z': speaker_info.get('z', 0.0),
            'dynamic': False
        }
        static_rows.append(row)
        static_count += 1
    
    # Process audio objects
    for obj_name, blocks in data.get('objectData', {}).items():
        if not blocks:
            continue
        
        # Determine if object is dynamic
        is_dynamic = False
        if len(blocks) > 1:
            # Check if positions change
            first_pos = (blocks[0].get('x', 0), blocks[0].get('y', 0), blocks[0].get('z', 0))
            has_movement = any(
                (b.get('x', 0), b.get('y', 0), b.get('z', 0)) != first_pos 
                for b in blocks
            )
            is_dynamic = has_movement
        
        if is_dynamic:
            dynamic_count += 1
            target_list = dynamic_rows
        else:
            static_count += 1
            target_list = static_rows
        
        # Add all position blocks with timestamps
        for block in blocks:
            time_seconds = parseTimecodeToSeconds(block.get('rtime', '00:00:00.00000'))
            row = {
                'id': obj_name,
                'time': round(time_seconds, 2),
                'x': block.get('x', 0.0),
                'y': block.get('y', 0.0),
                'z': block.get('z', 0.0),
                'dynamic': is_dynamic
            }
            target_list.append(row)
    
    # Sort static rows by id, then by time
    static_rows.sort(key=lambda r: (r['id'], r['time']))
    
    # Sort dynamic rows by id, then by time
    dynamic_rows.sort(key=lambda r: (r['id'], r['time']))
    
    # Combine: all static first, then all dynamic
    all_rows = static_rows + dynamic_rows
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['id', 'time', 'x', 'y', 'z', 'dynamic']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\nSpatial instructions CSV saved to {output_path}")
    print(f"  Total rows: {len(all_rows)}")
    print(f"  Static objects: {static_count} ({len(static_rows)} rows)")
    print(f"  Dynamic objects: {dynamic_count} ({len(dynamic_rows)} rows)")
    
    return len(all_rows)


if __name__ == "__main__":
    # Test the function
    row_count = createSpatialInstructionsCSV()
    print(f"\nCSV export complete with {row_count} rows")
