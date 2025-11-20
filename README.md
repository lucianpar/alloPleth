# ADM Decoder Prototype

This repository contains a Python prototype for exploring and decoding
Audio Definition Model Broadcast WAV (ADM BWF) files — atmos masters —
with mapping to the AlloSphere speaker layout.

## Quick Start

### 1. Clone and Initialize

```bash
git clone https://github.com/lucianpar/sonoPleth.git
cd sonoPleth
./init.sh
```

The `init.sh` script will:

- Create a Python virtual environment (`sonoPleth/`)
- Install all Python dependencies
- Install `bwfmetaedit` (via Homebrew)
- Initialize git submodules (AlloLib)
- Build the VBAP renderer

### 2. Get Example Files

```bash
python utils/getExamples.py
```

This downloads example Atmos ADM files for testing.

### 3. Run the Pipeline

```bash
# Default mode
python runPipeline.py

# With custom ADM file
python runPipeline.py path/to/atmos_file.wav

# Full options
python runPipeline.py <adm_wav_file> <speaker_layout.json> <true|false>
```

**Arguments:**

- `adm_wav_file` - Path to ADM BWF WAV file (Atmos master)
- `speaker_layout.json` - Speaker layout JSON (default: `vbapRender/allosphere_layout.json`)
- `true|false` - Create PDF analysis of render (default: `true`) -- recommended

## Troubleshooting

If you encounter dependency errors:

```bash
rm .init_complete
./init.sh
```

## Manual Setup

If `init.sh` fails, you can set up manually:

```bash
# 1. Create virtual environment
python3 -m venv sonoPleth
source sonoPleth/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install bwfmetaedit
brew install bwfmetaedit

# 4. Initialize submodules and build renderer
python3 -c "from src.configCPP import setupCppTools; setupCppTools()"
```

## Utilities

- `utils/deleteData.py` - Cleans processed data directory
- `utils/getExamples.py` - Downloads example ADM files

## Pipeline Overview

1. **Check Initialization** - Verify all dependencies are installed
2. **Setup C++ Tools** - Install bwfmetaedit, initialize AlloLib submodule, build VBAP renderer
3. **Extract Metadata** - Use bwfmetaedit to extract ADM XML from WAV
4. **Parse ADM** - Convert ADM XML to internal data structure
5. **Analyze Audio** - Detect which channels contain audio content
6. **Package for Render** - Split audio stems and create spatial instruction JSON
7. **VBAP Render** - Generate multichannel spatial audio using VBAP
8. **Analyze Render** - Create PDF with dB analysis of each output channel

## Testing Files

Example ADM files: https://zenodo.org/records/15268471

## Requirements

- macOS (for Homebrew installation of bwfmetaedit)
- Python 3.8+
- CMake and build tools
- Homebrew (for bwfmetaedit)
