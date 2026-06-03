# ESEE 2026 Research Project: Complete Context Document

**Project Name**: From Agent Choices to Policy Mandates: Bridging Micro-Behavioral Models and Degrowth Policy Implementation

**Target**: ESEE 2026 Conference (June 30–July 3, 2026), Track OSS8.6 [web:182]

**Timeline**: Abstract submission Jan 6, 2026; full implementation Jan–June 2026

**Acceptance Probability**: 65–70% (rough estimate based on strong track fit and methodological novelty) [web:182]

---

## SECTION 1: PROJECT OVERVIEW

### Research Question

How do heterogeneous household preferences for degrowth policies (estimated via causal machine learning from survey/choice data) translate into macroeconomic and distributional outcomes when used to parameterize an agent-based macro model for the EU?

### Why This Matters

Degrowth policies like shorter work weeks, reduced consumption, and circular economy transitions are discussed in EU policy, but there is little clarity on who would actually adopt them and how the macroeconomy would react. Standard macro models assume representative agents and often ignore behavioral diversity and political feasibility. This project directly addresses that gap by grounding macro simulations in empirically estimated behavioral heterogeneity.

### What Is Novel

- **Causal forests + ABM integration**: There is almost no work combining causal forest–style heterogeneous treatment effect estimation with macro-scale agent-based models for policy evaluation; most ABMs use hand-tuned behavioral rules, and most causal-ML papers stop at micro-level predictions. [web:257]
- **Behaviorally grounded degrowth macro modeling**: Degrowth and ecological macro papers rarely anchor agent behavior in large-scale micro evidence from surveys like the European Social Survey (ESS) or similar. [web:60][web:182]
- **Explicit link to ESEE Track OSS8.6**: That track calls for methods that bridge micro-behavioral dynamics and macro modeling, which this project does by design. [web:182]

### Expected Impact (Policy Implications)

- Quantify which degrowth policy mixes are behaviorally feasible (high expected uptake) versus politically fragile (limited uptake, strong distributional losers).
- Provide distributional profiles (by income, region, and sector) of winners and losers for multiple policy scenarios.
- Offer an operational framework EU policymakers can adapt when designing just transitions and Green Deal–style interventions.

---

## SECTION 2: THEORETICAL FRAMEWORK

### Ecological Economics Foundations

1. **Provisioning Systems / Needs-Based Welfare**
   - Focus on how societies organize systems of work, income, and infrastructure to meet human needs within ecological limits.
   - This project treats households as agents embedded in provisioning systems, whose work-time and consumption choices respond to policy and constraints.

2. **Ecological Macroeconomics**
   - Uses macro models that incorporate biophysical limits (emissions, material flows) and often non-growing or post-growth steady states.
   - The ABM includes emissions and sector structures compatible with multi-regional input–output data (e.g., Exiobase) to track environmental impact alongside employment and inequality. [web:257]

3. **Post-Growth / Degrowth**
   - Argues for deliberate reduction of throughput and, often, economic output in high-income countries, focusing on well-being rather than GDP growth.
   - Policies like work-time reduction, consumption caps, circular economy transitions, and UBI are modeled as explicit scenarios to test their political and distributional feasibility. [web:257]

4. **Behavioral Economics & Heterogeneity**
   - Moves beyond representative rational agents; recognizes that preferences and constraints differ across incomes, regions, and sectors.
   - Causal forests are used to estimate heterogeneous treatment effects for policy adoption, which are then used as behavior parameters in the ABM.

### How Causal ML + ABM Integration Advances These Theories

- Provides an empirically grounded way to connect provisioning theory (who can adopt what policies) with macro outcomes (employment, inequality, emissions).
- Avoids “representative agent” assumptions by explicitly encoding heterogeneity from survey/choice data.
- Allows ex ante policy analysis that is both distributionally explicit and behaviorally realistic, aligning with ecological macro goals of just, feasible transitions.

### Key Citations / Intellectual Lineage

*(You will fill the actual BibTeX later; here are short references to guide you.)*

- Athey, S. & Wager, S. (2019). “Generalized Random Forests” – methodology for heterogeneous treatment effects via forest-based models.  
- Gough, I. (2017). *Heat, Greed and Human Need* – provisioning systems and climate justice.  
- Jackson, T. (2009). *Prosperity Without Growth* – ecological macro and post-growth framing.  
- Farmer, J. D. et al. (2015). Work on agent-based and complexity approaches to climate and macroeconomics. [web:257]  
- D’Alisa, Demaria, Kallis (2014). *Degrowth: A Vocabulary for a New Era* – degrowth policy narratives.  
- Exiobase documentation – multi-regional input–output data for environmental footprinting.  

---

## SECTION 3: COMPLETE METHOD DESCRIPTION

### Component 1: Causal Forest for Heterogeneous Treatment Effects

**Goal**: Learn how different types of households (by income, region, sector, etc.) differ in their probability of adopting specific degrowth policies.

- **Inputs**
  - Micro data from a European survey or choice experiment (e.g., ESS-like data):  
    - Demographics (age, gender, education)  
    - Income proxies (income decile/quintile, or self-reported income band)  
    - Region (e.g., NUTS 2 or country dummies)  
    - Sector or employment status (industry codes where possible)  
    - Political/environmental attitudes (e.g., concern about climate, trust in institutions)
  - Policy outcome variables:
    - Binary indicators (0/1) like “would adopt reduced work time if policy introduced,” “would accept consumption cap,” etc., derived from survey questions.

- **Process**
  1. Clean and preprocess survey data: handle missing values, encode categorical variables, standardize or normalize features as needed.
  2. Define:
     - \( T \): “treatment” or policy framing (e.g., being offered a reduced working time option with some trade-off).
     - \( Y \): adoption / willingness-to-adopt indicator.
     - \( X \): covariates (demographics, income, region, sector, attitudes).
  3. Fit a causal forest / generalized random forest to estimate conditional average treatment effects (CATE), \(\tau(X)\).
  4. Aggregate CATEs by discrete “household types” (e.g., income quintile × region × sector) to get robust adoption probabilities for each type.
  5. Validate out-of-sample performance (R², RMSE on predicted probabilities, calibration plots).

- **Outputs**
  - Trained causal forest model object (saved model file).
  - Table / matrix with adoption probabilities:
    - For each relevant combination: (income group, region, sector, etc.) → \( P(\text{adopt policy} | X) \).
  - Visualizations:
    - Heatmaps of adoption probability by income vs. region.
    - Partial dependence / feature importance plots.

- **Why It Matters**
  - Provides realistic, data-based behavioral parameters for the ABM instead of arbitrary adoption rates.
  - Captures who is likely to comply with or support degrowth policies and who is not, which is essential for distributional and political feasibility analysis.

---

### Component 2: Agent-Based Model Calibration

**Goal**: Build a macro-scale ABM of the EU economy whose agents’ behavior (policy adoption) is governed by the causal-forest-derived heterogeneity.

- **Inputs**
  - Behavioral parameters: adoption probabilities by agent type from Component 1.
  - Macro/structural data:
    - Employment by sector and region (e.g., from EU-LFS). [web:258]
    - Income distribution by region and sector.
    - Production/emissions structure (e.g., from Exiobase I/O tables). [web:258]
  - Baseline 2023 EU macro conditions: aggregate employment, income, sector shares, emissions.

- **Agent Construction**
  - Number of agents: target ~1,000,000 synthetic households (downsampled to fit memory).
  - Each agent assigned:
    - Income group (e.g., quintile).
    - Region.
    - Sector or occupation.
    - Baseline working hours and consumption level.
    - Behavioral parameters: probability of adopting each policy per scenario, derived from causal forest for its type.

- **Environment & Initialization**
  - Environment encodes:
    - Sectors with production/employment.
    - Emissions factors per sector.
    - Policy parameters (when scenarios are switched on).
  - Baseline run (no policy):
    - Agents keep baseline hours and consumption.
    - Run ABM until macro variables stabilize (employment, income distribution, etc.).
    - Check that simulated baseline matches external data (EU stats) within tolerance (e.g., ±5%).

- **Outputs**
  - Calibrated ABM state representing a plausible EU 2023 baseline.
  - Calibration diagnostics (difference between simulated and actual aggregate stats).
  - Code and configuration files specifying how to recreate this baseline.

- **Why It Matters**
  - Ensures that policy scenarios start from a realistic, empirically grounded macro state.
  - Validates that the ABM can reproduce known macro patterns before introducing degrowth policies.

---

### Component 3: Policy Scenario Simulation

**Goal**: Simulate macro outcomes for different degrowth policy scenarios, driven by heterogeneous micro behavior.

- **Scenarios (illustrative set of 5)**
  1. **Baseline (no policy change)** – control scenario.
  2. **Work-Time Reduction** – e.g., policy to reduce standard full-time work from 40h to 30h per week.
  3. **Consumption Cap** – e.g., policy capping consumption or requiring a 15% reduction in certain categories.
  4. **Circular Economy Mandate** – e.g., regulations that push sectors into circular practice, affecting employment and sector composition.
  5. **Combined + UBI** – combination of reduced hours, consumption caps, circular mandate, and a modest universal basic income.

- **Process**
  1. For each scenario, define how policies change agents’ choice sets and constraints.
  2. At each time step:
     - Agents decide whether to adopt the policy (e.g., reduce hours, lower consumption) based on their assigned adoption probabilities.
     - Agent decisions feed into sector-level outcomes (labor demand, output, consumption).
     - Macro variables are updated (total employment, wages, consumption, emissions, inequality).
  3. Run each scenario for a fixed horizon (e.g., 100 steps representing multiple years).
  4. Record time series of:
     - Employment by sector and region.
     - Income distribution / inequality indicators (Gini, percentiles).
     - Emissions or resource use.
     - Measures of “political feasibility” (e.g., share of population adopting or benefiting).

- **Outputs**
  - Scenario results dataset: time series for all key indicators per scenario.
  - Comparative figures:
    - Employment trajectories by scenario.
    - Inequality trajectories by scenario.
    - Emissions trajectories by scenario.
  - Summary tables showing differences at the end of the horizon and/or at steady state.

- **Why It Matters**
  - Translates micro heterogeneity into macro consequences.
  - Shows how policy packages can be designed to be both ecologically effective and distributionally just (or not).

---

## SECTION 4: DATA INVENTORY (ABSTRACTED FOR PUBLIC USE)

Because micro data like ESS or EU-LFS usually require some registration, your actual implementation will use whichever public micro/choice dataset you can legally access that has:

- Individual-level demographics and income
- Attitudinal or choice responses to policy-like questions
- Regional and sector identifiers

You will need:

1. **Micro Survey/Choice Data (ESS-like)**
   - Variables: age, gender, education, income band, region, sector, climate concern, policy-related willingness questions.
   - Format: CSV or similar.
   - Size: ~50,000 observations or more.
   - Use: Train causal forest and derive adoption probabilities.

2. **Labor / Structural Data (EU-LFS-like)**
   - Variables: employment counts by region and sector, hours, maybe wage bands.
   - Use: Calibrate ABM sectoral and regional employment structure.

3. **Input–Output / Environmental Data (Exiobase-like)**
   - Multi-regional input–output table with environmental extensions.
   - Use: Map sector activity to emissions or resource use.

For each dataset, document:

- Source URL
- Format
- Access steps (registration or free download)
- Core variables used
- Any preprocessing steps (cleaning, recoding, harmonizing regions/sectors).

---

## SECTION 5: TECHNICAL ARCHITECTURE (ABSTRACT VERSION)

Even without installing anything yet, the architecture is:

- **Language**: Python 3.11+
- **Main Libraries**:
  - pandas, numpy, scikit-learn (for data + ML)
  - a causal-ML package or your own causal-forest implementation
  - Mesa (or similar) for agent-based modeling
  - matplotlib/seaborn for plots
  - pytest for tests

- **Folder Layout**
  - `config/` – YAML/JSON configs for data paths and hyperparameters
  - `data/raw/` – downloaded datasets
  - `data/processed/` – cleaned/merged data and train/test splits
  - `src/` – all scripts (data, causal forest, ABM, scenarios, baselines, plots)
  - `notebooks/` – exploratory notebooks
  - `results/` – figures, tables, model outputs, logs
  - `paper/` – LaTeX or manuscript source

The idea is to keep **data, code, results, and paper** separated and reproducible.

---

## SECTION 6: EXPECTED OUTPUTS (CHECKLIST FORM)

By the time you’re writing the paper, you want to have:

- **Causal Forest Outputs**
  - Trained model file
  - Adoption probability tables by type
  - Validation metrics (R², RMSE, calibration)

- **ABM Outputs**
  - Baseline calibration diagnostics
  - Scenario simulation results (5 scenarios × 100 timesteps)

- **Figures (for the paper)**
  - Heterogeneous adoption heatmap
  - ABM architecture diagram
  - Policy scenario comparison plots
  - Distributional impact plots (by income/region)
  - Baseline vs. our method comparison
  - Ablation results

- **Tables**
  - Summary statistics (data)
  - Model validation metrics (causal forest and ABM)
  - Policy outcomes per scenario
  - Baselines and ablations

This file (`ESEE2026_PROJECT_CONTEXT.md`) is what you give to a coding assistant or reviewer so they fully understand the project, even if they weren’t there when it was conceived.
