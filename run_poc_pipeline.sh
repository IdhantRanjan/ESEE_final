#!/bin/bash
# ESEE 2026 Proof-of-Concept Pipeline Runner
# Runs all POC steps in sequence

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "ESEE 2026 PROOF-OF-CONCEPT PIPELINE"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: ESS Data Preparation
echo "STEP 1/4: ESS Minimal Data Preparation"
echo "────────────────────────────────────────"
python3 src/poc_01_ess_minimal_prep.py
echo ""

# Step 2: Causal Forest
echo "STEP 2/4: Simple Causal Forest"
echo "────────────────────────────────────────"
python3 src/poc_02_causal_forest_minimal.py
echo ""

# Step 3: Toy ABM
echo "STEP 3/4: Toy Agent-Based Model"
echo "────────────────────────────────────────"
python3 src/poc_03_toy_abm.py
echo ""

# Step 4: Summary Report
echo "STEP 4/4: Generate Summary Report"
echo "────────────────────────────────────────"
python3 src/poc_04_generate_summary.py
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "PIPELINE COMPLETE!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Check results/logs/poc_summary_report.txt for summary"
echo "Check results/figures/ for visualizations"
echo "Check results/tables/ for data tables"
echo ""
echo "═══════════════════════════════════════════════════════════"


