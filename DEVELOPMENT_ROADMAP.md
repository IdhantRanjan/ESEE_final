# COMPLETE DEVELOPMENT ROADMAP: ESEE 2026 RESEARCH IMPLEMENTATION

This file defines a concrete, step-by-step plan to implement the project described in `ESEE2026_PROJECT_CONTEXT.md`. It is written so that an AI coding assistant (like Cursor) can implement each step as a separate script.

---

## GLOBAL PROJECT STRUCTURE

Target folder: `esee2026_degrowth_abm/`

Top-level structure (once everything is created):

- `ESEE2026_PROJECT_CONTEXT.md` – overall understanding
- `DEVELOPMENT_ROADMAP.md` – this roadmap
- `QUICK_START_GUIDE.md` – how to run everything
- `config/`
- `data/raw/`
- `data/processed/`
- `src/`
- `src/utils/`
- `tests/`
- `results/`
- `results/logs/`
- `results/figures/`
- `results/tables/`
- `results/model_outputs/`
- `paper/`

Each step below has:

- Name
- Goal
- Inputs / outputs
- What the script in `src/` should do
- Validation tests

Use this as a checklist and as instructions for the coding assistant.

---

## STEP 0: ENVIRONMENT SETUP & VERIFICATION

**Goal**: Create a Python environment and minimal project skeleton.

**Script(s)**: (you can hand-create these)

- `src/00_setup.py` – prints Python version and verifies imports as they’re added.

**Outputs**:

- A working virtual environment
- Confirmation that Python runs in this project

**Validation**:

- Run `python src/00_setup.py` and see a printed Python version.

---

## STEP 1: DATA ACQUISITION – SURVEY / CHOICE DATA

**Goal**: Make sure micro/choice data (ESS-like) is present in `data/raw/` as a CSV.

**Script**: `src/01_data_acquisition.py`

**Responsibilities**:

- Check for `data/raw/ESS_like_survey.csv` (you can rename it once you have a real file).
- If missing, print instructions to the user on how to manually download it.
- If present, load it, print shape and key columns, and write a short “download report” text file.

**Inputs**:

- None (you will manually place the CSV into `data/raw/`).

**Outputs**:

- `data/raw/ESS_like_survey.csv` (manually placed)
- `data/raw/ess_like_download_report.txt` – shape + simple checks.

**Validation**:

- Running `python src/01_data_acquisition.py` should:
  - Detect the file
  - Print row/column counts
  - Confirm presence of core columns (income, region, policy adoption questions)

---

## STEP 2: DATA ACQUISITION – LABOR / STRUCTURAL DATA

**Goal**: Ensure labor/structural data (EU-LFS-like) is present.

**Script**: same `src/01_data_acquisition.py` or a new one (`src/01b_data_acquisition_structural.py`).

**Responsibilities**:

- Check for `data/raw/lfs_like_structural.csv`.
- If missing, print manual download instructions.
- If present, validate shape and key variables (region, sector, employment).

**Outputs**:

- `data/raw/lfs_like_structural.csv`
- Simple validation/summary in a text file.

---

## STEP 3: DATA ACQUISITION – I/O / ENVIRONMENTAL DATA

**Goal**: Ensure input–output / environmental data (Exiobase-like) is present.

**Script**: `src/01c_data_acquisition_io.py` (or integrated into Step 1).

**Outputs**:

- `data/raw/io_like_matrix.csv` or `.xlsx`
- Environmental extensions file if available
- Validation summary (matrix dimensions, no weird negative values, etc.)

---

## STEP 4: DATA PREPROCESSING – SURVEY DATA

**Goal**: Clean micro survey data, create binary adoption outcomes and covariates.

**Script**: `src/02_data_preprocessing_survey.py`

**Responsibilities**:

- Load `data/raw/ESS_like_survey.csv`.
- Filter to relevant countries/regions (e.g., EU members).
- Create:
  - Income group variable (e.g., quintiles).
  - Binary outcomes from Likert questions (e.g., willingness ≥ threshold ⇒ 1).
  - Encoded region, sector, and other categorical covariates.
- Handle missing values (drop or impute consistently).
- Save cleaned dataset to `data/processed/ess_processed.csv`.

**Validation**:

- `ess_processed.csv` has expected number of rows (no catastrophic loss).
- Adoption variables are 0/1 and have reasonable rates (e.g., 0.3–0.8).

---

## STEP 5: DATA PREPROCESSING – STRUCTURAL LABOR DATA

**Goal**: Aggregate labor data to region×sector and compute shares and reference employment.

**Script**: `src/02b_data_preprocessing_structural.py`

**Responsibilities**:

- Load `data/raw/lfs_like_structural.csv`.
- Create region×sector employment totals and shares.
- Maybe compute unemployment rates by region.
- Save to `data/processed/lfs_processed.csv`.

**Validation**:

- `lfs_processed.csv` has one row per region×sector.
- Shares sum to ~1 per region.

---

## STEP 6: DATA PREPROCESSING – I/O / ENVIRONMENTAL DATA

**Goal**: Convert raw I/O tables into convenient Python objects.

**Script**: `src/02c_data_preprocessing_io.py`

**Responsibilities**:

- Load I/O table file.
- Map sectors in I/O to the sector classification used in the labor data (possibly via a mapping table).
- Extract emissions or resource-use coefficients per sector.
- Save processed structures to `data/processed/io_processed.pkl` (e.g., a dict of matrices).

**Validation**:

- Matrices have expected dimensions (e.g., sectors×sectors).
- Coefficients are non-negative and plausible.

---

## STEP 7: DATA MERGING – FINAL ANALYTICAL DATASET

**Goal**: Create the dataset used for causal forest training.

**Script**: `src/02d_data_merge_for_cf.py`

**Responsibilities**:

- Load `ess_processed.csv`.
- Merge in regional/sectoral variables (e.g., unemployment rate from `lfs_processed.csv`).
- Possibly merge high-level I/O-based sector labels.
- Split into train and test sets and save:
  - `data/processed/merged_data.csv`
  - `data/processed/train_test_split.pkl`

**Validation**:

- Merged dataset has the same number of rows as the survey data.
- Train/test splits have expected sizes (e.g., 70/30).

---

## STEP 8: EXPLORATORY DATA ANALYSIS

**Goal**: Understand distributions and check for obvious issues.

**Script**: `src/03_exploratory_analysis.py`

**Responsibilities**:

- Load merged data.
- Produce:
  - Summary statistics for key variables.
  - Histograms for income, adoption variables.
  - Simple correlation heatmaps.
- Save plots to `results/figures/eda_*.png`.

**Validation**:

- Figures generated without error.
- No obviously broken distributions (e.g., all zeros).

---

## STEP 9: FEATURE ENGINEERING FOR CAUSAL FOREST

**Goal**: Prepare X, T, Y matrices/vectors for causal forest.

**Script**: `src/04_feature_engineering_cf.py`

**Responsibilities**:

- Load merged data and train/test split.
- Define:
  - Y: adoption outcome (binary).
  - T: treatment indicator (or policy framing, if available).
  - X: covariates (demographics, income, region, sector, attitudes).
- Encode categoricals and scale if necessary.
- Save to `data/processed/cf_features.pkl`.

**Validation**:

- X has no missing values.
- Shapes of (X, T, Y) match expectations.

---

## STEP 10: CAUSAL FOREST TRAINING

**Goal**: Train the causal forest model and evaluate it.

**Script**: `src/04_causal_forest.py`

**Responsibilities**:

- Load `cf_features.pkl`.
- Train a causal forest / generalized random forest on the training set.
- Evaluate on the test set (R², RMSE, calibration).
- Save:
  - Model to `results/model_outputs/causal_forest.pkl`.
  - Metadata to `results/model_outputs/causal_forest_metadata.json`.
  - Validation plots to `results/figures/causal_forest_*.png`.

**Validation**:

- Model file exists and can be loaded.
- Metrics within acceptable ranges (not trivial or broken).

---

## STEP 11: EXTRACT HETEROGENEOUS TREATMENT EFFECTS

**Goal**: Turn causal forest predictions into adoption probabilities by agent type.

**Script**: `src/04b_cf_extract_effects.py`

**Responsibilities**:

- Load causal forest model and full feature data.
- Define discrete “types” (e.g., income quintile × region × sector).
- For each type, compute average predicted adoption probability.
- Save:
  - A table `results/tables/cf_treatment_effects_by_type.csv`.
  - Heatmaps to `results/figures/cf_heatmaps_*.png`.

**Validation**:

- Probabilities between 0 and 1.
- Patterns are plausible (e.g., higher income may adopt some policies more readily, etc., depending on data).

---

## STEP 12: ABM – ARCHITECTURE DESIGN

**Goal**: Define the ABM classes: agents, environment, scheduler, and data collection.

**Script**: `src/05_abm_setup.py`

**Responsibilities**:

- Define:
  - Agent class with attributes (income, region, sector, behavioral parameters).
  - Model/environment class with:
    - Sectors and regions.
    - Global parameters (policy on/off flags).
- Prepare functions for:
  - Adding agents.
  - Stepping through time.
  - Collecting macro indicators.

**Validation**:

- A small test run with 1,000 agents and 10 timesteps runs without error.

---

## STEP 13: ABM – AGENT INITIALIZATION

**Goal**: Create 1M agents with types consistent with data.

**Script**: `src/05b_abm_initialize_agents.py`

**Responsibilities**:

- Use structural data (labor) to set regional/sector distribution.
- Use income distribution to set income categories.
- Use treatment effect table to assign adoption probabilities to agent types.
- Save the initialized model or a snapshot to `results/model_outputs/abm_initial_state.pkl`.

**Validation**:

- Number of agents ≈ target count.
- Aggregated agent distributions match external data (within tolerance).

---

## STEP 14: ABM – BASELINE CALIBRATION

**Goal**: Run a no-policy scenario and tune to match EU baseline.

**Script**: `src/06_abm_calibration.py`

**Responsibilities**:

- Run the ABM for a baseline scenario (no degrowth policies).
- Track:
  - Employment by sector and region.
  - Income distribution.
  - Optional emissions.
- Compare to external reference values.
- Adjust simple parameters (e.g., productivity, baseline hours) until error is small (≤ ~5%).

**Validation**:

- Calibration report (difference between simulated and actual).
- Baseline outputs stable over time (convergence).

---

## STEP 15–19: POLICY SCENARIOS

**Goal**: Implement and simulate 5 policy scenarios.

**Script**: `src/07_policy_scenarios.py`

**Responsibilities**:

- Implement scenario toggles and update rules:
  1. Baseline
  2. Work-time reduction
  3. Consumption cap
  4. Circular economy mandate
  5. Combined + UBI
- For each scenario:
  - Run ABM for 100 timesteps.
  - Save macro time series for:
    - Employment
    - Inequality
    - Emissions
- Save results to:
  - `results/model_outputs/policy_scenarios.pkl`
  - Figures to `results/figures/policy_scenarios_*.png`

**Validation**:

- All runs complete.
- Macros are bounded and plausible (no crazy explosions).

---

## STEP 20–22: BASELINES

**Goal**: Provide comparison methods to show value of heterogeneity & ABM.

**Script**: `src/08_baselines.py`

**Baseline ideas**:

1. Simple macro model with representative agents.
2. ABM with random/uniform adoption probabilities.
3. ABM using only average treatment effect (no heterogeneity).

**Outputs**:

- `results/model_outputs/baseline_methods.pkl`
- Comparison tables in `results/tables/baseline_comparison.csv`.

---

## STEP 23–25: ABLATIONS & ROBUSTNESS

**Goal**: Test importance of each component and robustness to parameter changes.

**Script**: `src/09_ablations.py`, `src/10_statistical_tests.py`

**Responsibilities**:

- Remove/modify:
  - Heterogeneity (force uniform adoption).
  - Regional variation.
  - Sector detail.
- Run multiple seeds / bootstrapped runs.
- Save:
  - `results/tables/ablation_results.csv`
  - `results/tables/sensitivity_analysis.csv`
  - Figures for ablation comparisons.

---

## STEP 26–28: VISUALIZATION & TABLES

**Goal**: Generate paper-ready figures and tables.

**Script**: `src/11_visualization.py`

**Responsibilities**:

- Define a consistent style (colors, fonts, sizes).
- Generate:
  - Heterogeneity heatmaps.
  - Scenario comparison line plots.
  - Distributional impact bar/stack plots.
  - Baseline vs. our method comparisons.
  - Ablation results.

**Outputs**:

- All figures in `results/figures/figure_*.png`.
- All tables in `results/tables/table_*.csv`.

---

## STEP 29: PAPER WRITING

**Goal**: Convert results into a structured paper.

**Location**: `paper/`

**Responsibilities**:

- Create `paper/main.tex` with:
  - Introduction
  - Literature review
  - Method (Causal Forest + ABM)
  - Results (scenarios + distributional outcomes)
  - Discussion
  - Conclusion
- Include figures and tables.
- Ensure the paper can compile.

---

## STEP 30: FINAL CHECKS & SUBMISSION PREP

**Goal**: Make sure everything is reproducible and ready to share.

**Checklist**:

- Can run full pipeline from raw data to final results.
- Tests (if added) pass.
- Figures and tables match what is in the paper.
- README explains how to reproduce key results.

This roadmap is meant to be handed to a coding assistant; each step can be turned into one or more scripts with clear inputs and outputs.
