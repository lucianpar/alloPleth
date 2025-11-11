# ADM Decoder Prototype

This repository contains a Python prototype for exploring and decoding
Audio Definition Model Broadcast WAV (ADM BWF) files — atmos masters —
potential mapping the AlloSphere speaker layout.

### Setup

```bash
git clone https://github.com/lucianpar/sonoPleth.git
cd sonoPleth
python3 -m venv sonoPleth
source sonoPleth/bin/activate
pip install -r requirements.txt
```

# FOR TESTING

run main.py . terminal should output a metadata summary. in data/currentObjectData.json you can view a parsed version of the object metadata. there are also JSON files for the file's broad technical data and the direct speaker data (contains Low Frequency effect channel, direct surround channels, and dialogue - for film). the xml has the raw metadata

# Testing Files found at:

https://zenodo.org/records/15268471
