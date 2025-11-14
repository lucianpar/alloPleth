import json
import os
import csv

def loadProcessedData(processed_dir="processedData"):
    """Load all JSON files from processedData directory.
    
    Returns:
        dict: with 'globalData', 'directSpeakerData', and 'objectData'
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

    channels_contains_audio_path = os.path.join(processed_dir, "containsAudio.json")
    if os.path.exists(channels_contains_audio_path):
        with open(channels_contains_audio_path, 'r') as f:
            data['containsAudio'] = json.load(f)
        print(f"Loaded containsAudio from {channels_contains_audio_path}")
    else:
        data['containsAudio'] = {}
        print(f"Warning: {channels_contains_audio_path} not found")

    
    return data

def mapEmptyChannels(data):
    """Map which channels contain audio based on containsAudio data.
    
    Args:
        data (dict): Loaded processed data containing containsAudio info
    
    Returns:
        dict: Mapping of channel index -> contains_audio (True/False)
    """
    channel_audio_map = {}
    contains_audio_info = data.get('containsAudio', {})
    for channel_info in contains_audio_info.get('channels', []):
        channel_index = channel_info.get('channel_index')
        contains_audio = channel_info.get('contains_audio', False)
        channel_audio_map[channel_index] = contains_audio
    return channel_audio_map


def assignChannels(data):
    """Assign channel numbers to DirectSpeakers and objects.
    
    DirectSpeakers get channels 1-10 (in order of appearance)
    Objects get channels 11+ (in order of appearance in objectData)
    
    Args:
        data (dict): Loaded processed data containing directSpeakerData and objectData
    
    Returns:
        tuple: (channel_mapping dict, audio_status dict)
            - channel_mapping: name -> channel number
            - audio_status: name -> has_audio (True/False)
    """
    channel_mapping = {}
    audio_status = {}
    channel_counter = 1
    
    # Get audio status map (0-indexed)
    channel_audio_map = mapEmptyChannels(data)
    
    # Assign channels 1-10 to DirectSpeakers (in order)
    for speaker_name in data.get('directSpeakerData', {}).keys():
        channel_mapping[speaker_name] = channel_counter
        # Check if this channel (0-indexed in audio map) contains audio
        audio_status[speaker_name] = channel_audio_map.get(channel_counter - 1, False)
        channel_counter += 1
    
    # Assign channels 11+ to objects (in order, skip empty objects)
    for obj_name, blocks in data.get('objectData', {}).items():
        if blocks:  # Only assign channel if object has data
            channel_mapping[obj_name] = channel_counter
            # Check if this channel (0-indexed in audio map) contains audio
            audio_status[obj_name] = channel_audio_map.get(channel_counter - 1, False)
            channel_counter += 1
    
    print(f"\nChannel assignments:")
    print(f"  DirectSpeakers: channels 1-{len(data.get('directSpeakerData', {}))}")
    print(f"  Objects: channels {len(data.get('directSpeakerData', {})) + 1}-{channel_counter - 1}")
    print(f"  Total channels assigned: {len(channel_mapping)}")
    
    return channel_mapping, audio_status


def parseTimecodeToSeconds(timecode):
    """Convert timecode string (HH:MM:SS.SSSSS) to seconds."""
    try:
        hours, minutes, seconds = timecode.split(':')
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    except:
        return 0.0
    



def createSpatialInstructionsCSV(processed_dir="processedData", output_path="forExport/spatialInstructions.csv"):
    """Create spatial instructions CSV with timestamped position data.
    
    CSV format: channel,id,has_audio,time,x,y,z,dynamic
    - channel: numerical channel index (1-10 for DirectSpeakers, 11+ for objects)
    - id: object/speaker name
    - has_audio: True/False based on containsAudio.json
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
    
    # Assign channel numbers and get audio status
    channel_mapping, audio_status = assignChannels(data)
    
    static_rows = []
    dynamic_rows = []
    static_count = 0
    emptyStatic_count = 0
    dynamic_count = 0
    emptyDynamic_count = 0
    
    # Process DirectSpeakers as static objects (time = 0.00)
    for speaker_name, speaker_info in data.get('directSpeakerData', {}).items():
        row = {
            'channel': channel_mapping[speaker_name],
            'id': speaker_name,
            'has_audio': audio_status[speaker_name],
            'dynamic': False,
            'time': 0.00,
            'x': speaker_info.get('x', 0.0),
            'y': speaker_info.get('y', 0.0),
            'z': speaker_info.get('z', 0.0)
        }
        static_rows.append(row)
        static_count += 1
        if not audio_status[speaker_name]:
            emptyStatic_count += 1

    # Process audio objects
    for obj_name, blocks in data.get('objectData', {}).items():
        if not blocks:
            continue
        
        obj_channel = channel_mapping[obj_name]
        has_audio = audio_status[obj_name]
        
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
                'channel': obj_channel,
                'id': obj_name,
                'has_audio': has_audio,
                'dynamic': is_dynamic,
                'time': round(time_seconds, 2),
                'x': block.get('x', 0.0),
                'y': block.get('y', 0.0),
                'z': block.get('z', 0.0)
                
            }
            if not audio_status[obj_name]:
                emptyDynamic_count += 1
            target_list.append(row)
    
    # Sort static rows by channel, then by time
    static_rows.sort(key=lambda r: (r['channel'], r['time']))
    
    # Sort dynamic rows by channel, then by time
    dynamic_rows.sort(key=lambda r: (r['channel'], r['time']))
    
    # Combine: all static first, then all dynamic
    all_rows = static_rows + dynamic_rows
    
    # Write to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['channel', 'id', 'has_audio', 'dynamic', 'time', 'x', 'y', 'z']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\nSpatial instructions CSV saved to {output_path}")
    print(f"  Total rows: {len(all_rows)}")
    print(f"  Static objects: {static_count}({len(static_rows)} rows), {emptyStatic_count} empty channels ")
    print(f"  Dynamic objects: {dynamic_count}({len(dynamic_rows)} rows),  {emptyDynamic_count} empty channels ")
    
    return len(all_rows)


# if __name__ == "__main__":
#     # Test the function
#     row_count = createSpatialInstructionsCSV()
#     print(f"\nCSV export complete with {row_count} rows")
