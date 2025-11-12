import subprocess
import os

def extractMetaData(wavPath, outXmlPath):
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
        print(" ERROR bwfmetaedit NOT found — make sure it’s installed and on PATH.")

    return outXmlPath

# Example usage
# wavFilePath = "../data/POE-ATMOS-FINAL.wav"
# xmlFilePath = "../data/newPOETest-metadata.xml"

# extractMetaData(wavFilePath, xmlFilePath)

