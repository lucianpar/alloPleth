import subprocess
import os

def extractMetaData(wavPath, outXmlPath):
    print("Extracting ADM metadata from WAV file...")
    """Run bwfmetaedit on a .wav file and export its ADM XML."""
    cmd = [
        "bwfmetaedit",
        f"--out-xml={outXmlPath}",
        wavPath 
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Exported ADM metadata to {outXmlPath }")
    except subprocess.CalledProcessError as e:
        print(f" ERROR running bwfmetaedit: {e}")
    except FileNotFoundError:
        print(" ERROR bwfmetaedit NOT found!")
        print(" Install with: brew install bwfmetaedit")
        print(" Or download from: https://mediaarea.net/BWFMetaEdit")
        print(" Alternatively, run: from src.configCPP import installBwfmetaedit; installBwfmetaedit()")

    return outXmlPath



