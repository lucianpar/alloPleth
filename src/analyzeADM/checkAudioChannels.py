import os
import json
import numpy as np
import soundfile as sf
import time

def channelHasAudio(file_path, threshold_db=-100, chunk_size=48000, printChannelUpdate=True):
    """Check which channels of an audio file contain audio above a threshold (in dBFS).
    
    Uses chunked processing for speed - samples audio in chunks rather than loading entire file.
    Prints progress and total time taken.
    """
    info = sf.info(file_path)
    sr = info.samplerate
    channels = info.channels
    total_frames = info.frames
    
    num_samples = 30 #fine tuning for speed vs accuracy. not sure about ideal value
    skip = max(1, total_frames // (chunk_size * num_samples))
    
    active_data = []
    start_time = time.time()
    
    print(f"Scanning {channels} channels in '{file_path}'...")
    
    for channelIndex in range(channels):
        max_rms_db = -np.inf

        for chunkIndex in range(num_samples):
            start_frame = chunkIndex * skip * chunk_size
            if start_frame >= total_frames:
                break
            
            frames_to_read = min(chunk_size, total_frames - start_frame)
            chunk = sf.read(file_path, start=start_frame, frames=frames_to_read, always_2d=True)
            channel_data = chunk[0][:, channelIndex]
            rms = np.sqrt(np.mean(channel_data ** 2))
            rms_db = 20 * np.log10(rms + 1e-10)
            if rms_db > max_rms_db:
                max_rms_db = rms_db
            if max_rms_db > threshold_db:
                break
        
        active = max_rms_db > threshold_db
        active_data.append({
            "channel_index": channelIndex,
            "rms_db": round(float(max_rms_db), 2),
            "contains_audio": bool(active)
        })
        if printChannelUpdate:
            print(f"  Channel {channelIndex+1}/{channels} scanned (rms_db={round(float(max_rms_db),2)}, contains_audio={active})")
    
    elapsed = time.time() - start_time
    print(f"Scan complete: {channels} channels processed in {elapsed:.2f} seconds.")
    
    return {"sample_rate": sr, "threshold_db": threshold_db, "channels": active_data, "elapsed_seconds": round(elapsed, 2)}

def deleteContainsAudioJSON(output_path="processedData/containsAudio.json"):
    """
    Delete the containsAudio.json file if it exists.
    """
    file_path = os.path.abspath(output_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")
    else:
        print(f"No file to delete at: {file_path}")

def exportAudioActivity(file_path, output_path="processedData/containsAudio.json", threshold_db=-100):
    """Process a file and save per-channel activity info as JSON."""
    deleteContainsAudioJSON(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = channelHasAudio(file_path, threshold_db)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    print(f"Saved channel activity to {output_path}")


