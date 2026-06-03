# ESEE 2026 Degrowth ABM Project

**Project Name**: From Agent Choices to Policy Mandates: Bridging Micro-Behavioral Models and Degrowth Policy Implementation

**Target**: ESEE 2026 Conference (June 30–July 3, 2026), Track OSS8.6

## Quick Start

1. **Run setup script:**
   ```bash
   python src/00_setup.py
   ```

2. **Create and activate virtual environment:**
   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

3. **Activate virtual environment (for future sessions):**
   ```bash
   source venv/bin/activate
   ```

## Project Structure

- `src/` - All Python scripts
- `data/raw/` - Raw datasets (ESS, LFS, Exiobase)
- `data/processed/` - Cleaned and merged data
- `results/` - Outputs (figures, tables, model outputs, logs)
- `tests/` - Unit tests
- `paper/` - LaTeX paper source
- `config/` - Configuration files
- `notebooks/` - Jupyter notebooks for exploration

## Documentation

- `ESEE2026_PROJECT_CONTEXT.md` - Complete project overview and methodology
- `DEVELOPMENT_ROADMAP.md` - Step-by-step implementation guide
- `QUICK_START_GUIDE.md` - Getting started instructions

## Methodology

This project combines:
1. **Causal Forest** - Estimates heterogeneous treatment effects for degrowth policy adoption from survey data
2. **Agent-Based Model** - Simulates macro outcomes using empirically-grounded behavioral parameters
3. **Policy Scenarios** - Evaluates 5 degrowth policy scenarios with distributional analysis

## Requirements

- Python 3.11+
- See `requirements.txt` for full package list

## License

[To be determined]

