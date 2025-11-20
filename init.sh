#!/bin/bash
# init.sh - Complete setup script for sonoPleth project
# This script handles:
# 1. Python virtual environment creation
# 2. Python dependencies installation
# 3. C++ tools setup (bwfmetaedit, allolib submodules, VBAP renderer build)

set -e  # Exit on any error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "sonoPleth Initialization"
echo "============================================================"
echo ""

# Step 1: Create Python virtual environment
echo "Step 1: Setting up Python virtual environment..."
if [ -d "sonoPleth/bin" ]; then
    echo "✓ Virtual environment already exists at sonoPleth/"
else
    echo "Creating virtual environment..."
    python3 -m venv sonoPleth
    echo "✓ Virtual environment created"
fi
echo ""

# Step 2: Activate virtual environment and install Python dependencies
echo "Step 2: Installing Python dependencies..."
source sonoPleth/bin/activate

if pip install -r requirements.txt; then
    echo "✓ Python dependencies installed"
else
    echo "✗ Error installing Python dependencies"
    exit 1
fi
echo ""

# Step 3: Setup C++ tools using Python script
echo "Step 3: Setting up C++ tools (bwfmetaedit, allolib, VBAP renderer)..."
if python3 -c "from src.configCPP import setupCppTools; exit(0 if setupCppTools() else 1)"; then
    echo "✓ C++ tools setup complete"
else
    echo "⚠ Warning: C++ tools setup had issues, but continuing..."
    echo "  You may need to manually install bwfmetaedit: brew install bwfmetaedit"
fi
echo ""

# Step 4: Create initialization flag file
echo "Step 4: Creating initialization flag..."
cat > .init_complete << EOF
# sonoPleth initialization complete
# Generated: $(date)
# Python venv: sonoPleth/
# This file indicates that init.sh has been run successfully.
# Delete this file to force re-initialization.
EOF

echo "✓ Initialization flag created (.init_complete)"
echo ""

echo "============================================================"
echo "✓ Initialization complete!"
echo "============================================================"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source sonoPleth/bin/activate"
echo ""
echo "To run the pipeline:"
echo "  python3 runPipeline.py <sourceADMFile> [sourceSpeakerLayout]"
echo ""
echo "If you encounter dependency errors, delete .init_complete and re-run:"
echo "  rm .init_complete && ./init.sh"
echo ""
