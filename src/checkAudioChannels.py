import os
import json
import numpy as np
import soundfile as sf

def channelHasAudio(file_path, threshold_db=-60):
    """Check which channels of an audio file contain audio above a threshold (in dBFS)."""
    y, sr = sf.read(file_path, always_2d=True)
    active_data = []

    for i in range(y.shape[1]):
        channel = y[:, i]
        rms = np.sqrt(np.mean(channel ** 2))
        rms_db = 20 * np.log10(rms + 1e-10)
        active = rms_db > threshold_db

        active_data.append({
            "channel_index": i,
            "rms_db": round(float(rms_db), 2),
            "contains_audio": bool(active)
        })

    return {"sample_rate": sr, "threshold_db": threshold_db, "channels": active_data}

def exportAudioActivity(file_path, output_path="processedData/containsAudio.json", threshold_db=-60):
    """Process a file and save per-channel activity info as JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result = channelHasAudio(file_path, threshold_db)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    print(f" Saved channel activity to {output_path}")


