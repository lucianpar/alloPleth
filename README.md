# ADM Decoder Prototype

This repository contains a Python prototype for exploring and decoding
Audio Definition Model Broadcast WAV (ADM BWF) files — such as Dolby Atmos masters —
for potential mapping the AlloSphere speaker layout.

### Structure

- `src/parser.py` – extracts and parses `axml` / `iXML` metadata.
- `src/decoder_core.py` – builds object and bed data structures.
- `src/visObjects.py` – plots object positions and trajectories.
- `notebooks/01_parse_ADM.ipynb` – step-by-step walkthrough and documentation.

### Setup

```bash
python3 -m venv atmosDecoder-env
source atmosDecoder-env/bin/activate
pip install -r requirements.txt
```
