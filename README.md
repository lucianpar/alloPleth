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

# FOR GETTING EXAMPLE FILES

Run:
python utils/getExamples.py

This will download some boring but functional example Atmos files for running this project. Will add my own to this shortly

# USAGE FILES:

in terminal run:

python runPipeline.py [atmos adm wav file path]
OR
python runPipeline.py [atmos adm wav file path] [speaker layout json file path] [true / false for creating pdf analysis of final render]
OR
python runPipeline.py for default

- utils/deleteData.py - deletes data in processedData ( and spatialInstructions.csv?)

# PIPELINE SPECIFICS

# 1. set source

# 2. extract ADM metadata from source wav

# 3. parse ADM metadata into internal data structure (optionally export json for analysis)

# 4. analyze audio channels for content (generate containsAudio.json)

# 5. run packageForRender - this runs repackage (split stems) and createRenderInfo (spatial instructions json)

# 6. run create render - runs allolib vbap renderer to create spatial render

# 7. run analyze render -- creates pdf in processedData/ to show db analysis of each channel in final render

# Testing Files found at:

https://zenodo.org/records/15268471
