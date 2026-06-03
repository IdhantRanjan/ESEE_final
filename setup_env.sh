#!/bin/bash
# ESEE 2026 Degrowth ABM Project - Virtual Environment Setup Script
# This script creates a Python virtual environment and installs all required packages

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (project root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "ESEE 2026 Degrowth ABM - Virtual Environment Setup"
echo "============================================================"
echo ""

# Step 1: Check if Python is available
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Error: python3 not found. Please install Python 3.11+ first.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
echo ""

# Step 2: Check if venv already exists
VENV_DIR="$SCRIPT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "Step 2: Virtual environment already exists at $VENV_DIR"
    read -p "Do you want to remove it and create a fresh one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
        echo -e "${GREEN}✓ Removed old virtual environment${NC}"
    else
        echo "Using existing virtual environment."
    fi
fi

# Step 3: Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Step 3: Creating virtual environment..."
    if python3 -m venv "$VENV_DIR"; then
        echo -e "${GREEN}✓ Virtual environment created at $VENV_DIR${NC}"
    else
        echo -e "${RED}✗ Error: Failed to create virtual environment${NC}"
        exit 1
    fi
else
    echo "Step 3: Using existing virtual environment"
fi
echo ""

# Step 4: Activate virtual environment
echo "Step 4: Activating virtual environment..."
source "$VENV_DIR/bin/activate"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Error: Failed to activate virtual environment${NC}"
    exit 1
fi
echo ""

# Step 5: Upgrade pip
echo "Step 5: Upgrading pip..."
if pip install --upgrade pip --quiet; then
    echo -e "${GREEN}✓ pip upgraded successfully${NC}"
else
    echo -e "${RED}✗ Error: Failed to upgrade pip${NC}"
    exit 1
fi
echo ""

# Step 6: Check if requirements.txt exists
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${YELLOW}⚠ Warning: requirements.txt not found${NC}"
    echo "Running src/00_setup.py to generate it..."
    if python3 "$SCRIPT_DIR/src/00_setup.py"; then
        echo -e "${GREEN}✓ Generated requirements.txt${NC}"
    else
        echo -e "${RED}✗ Error: Failed to generate requirements.txt${NC}"
        exit 1
    fi
    echo ""
fi

# Step 7: Detect Apple Silicon (M-series Mac)
ARCH=$(uname -m)
USE_BREAK_SYSTEM_PACKAGES=""
if [ "$ARCH" = "arm64" ] && [ "$(uname -s)" = "Darwin" ]; then
    echo "Step 6: Detected Apple Silicon (M-series Mac)"
    echo "Using --break-system-packages flag for compatibility..."
    USE_BREAK_SYSTEM_PACKAGES="--break-system-packages"
    echo ""
fi

# Step 8: Install packages from requirements.txt
echo "Step 7: Installing packages from requirements.txt..."
if pip install -r "$REQUIREMENTS_FILE" $USE_BREAK_SYSTEM_PACKAGES; then
    echo -e "${GREEN}✓ All packages installed successfully${NC}"
else
    echo -e "${RED}✗ Error: Failed to install some packages${NC}"
    echo "You may need to install them manually or check for compatibility issues."
    exit 1
fi
echo ""

# Step 9: Verify installations
echo "Step 8: Verifying key package installations..."
KEY_PACKAGES=("pandas" "numpy" "sklearn" "econml" "mesa" "matplotlib" "seaborn")
ALL_OK=true

for package in "${KEY_PACKAGES[@]}"; do
    if pip show "$package" &> /dev/null; then
        VERSION=$(pip show "$package" | grep Version | cut -d' ' -f2)
        echo -e "${GREEN}✓ $package ($VERSION)${NC}"
    else
        echo -e "${RED}✗ $package not found${NC}"
        ALL_OK=false
    fi
done
echo ""

# Final summary
echo "============================================================"
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ SETUP COMPLETE${NC}"
else
    echo -e "${YELLOW}⚠ SETUP COMPLETE WITH WARNINGS${NC}"
fi
echo "============================================================"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
echo ""

