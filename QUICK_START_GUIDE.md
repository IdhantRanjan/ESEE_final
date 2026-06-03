
# QUICK START GUIDE: ESEE 2026 DEGROWTH PROJECT

This is the “how do I actually use this” file.

You already have:

- `ESEE2026_PROJECT_CONTEXT.md` – what the project is and why it matters.
- `DEVELOPMENT_ROADMAP.md` – what needs to be built.
- This guide – how to move from zero to working code.

---

## 1. FOLDER SETUP (MANUAL)

1. Create a folder somewhere, e.g.:

mkdir -p ~/esee2026_degrowth_abm
cd ~/esee2026_degrowth_abm

text

2. Inside that folder, create three files and paste:
- `ESEE2026_PROJECT_CONTEXT.md` – paste from the first big block.
- `DEVELOPMENT_ROADMAP.md` – paste from the second big block.
- `QUICK_START_GUIDE.md` – this file.

3. Open that folder in Cursor (or your editor).

---

## 2. MINIMUM VIABLE PYTHON SKELETON

You do NOT have to get fancy at the beginning. Start with:

1. Create folder structure:

mkdir -p src data/raw data/processed results/logs

text

2. Create a minimal Python file:

- File: `src/00_setup.py`  
- Contents:

import sys
import platform

def main():
print("Python version:", sys.version)
print("Platform:", platform.platform())
print("ESEE 2026 project skeleton is alive.")

if name == "main":
main()

text

3. Run it:

python src/00_setup.py

text

If it prints the version and “skeleton is alive”, you’re good.

---

## 3. HOW TO USE WITH CURSOR

You want Cursor to:

- Know the **project context**.
- Follow the **roadmap steps**.

Basic pattern:

1. Open the project in Cursor.
2. In a new chat, tell Cursor something like:

> “Here is my project context from `ESEE2026_PROJECT_CONTEXT.md` and `DEVELOPMENT_ROADMAP.md`. I want you to implement STEP 4 (Data preprocessing – survey) as `src/02_data_preprocessing_survey.py`. Use pandas, assume input file `data/raw/ESS_like_survey.csv`, output `data/processed/ess_processed.csv`, and include simple logging and validation.”

3. Paste the relevant step description from `DEVELOPMENT_ROADMAP.md` so Cursor has instructions.
4. Cursor will generate code; you save it to the correct file and run it.

Repeat this pattern step by step.

---

## 4. HIGH-LEVEL TIMELINE (REALISTIC)

Assuming ~1 hour/day:

- **Days 1–3**:  
- Set up folder and files.  
- Create `src/00_setup.py`, maybe a venv.  
- Ensure Python runs.

- **Days 4–7**:  
- Put survey/labor/I-O data into `data/raw/`.  
- Implement Steps 1–3 (acquisition/validation).

- **Days 8–12**:  
- Implement Steps 4–7 (preprocessing + merge).  
- Run EDA (Step 8).

- **Days 13–17**:  
- Implement Steps 9–11 (causal forest and treatment-effect extraction).

- **Days 18–24**:  
- Implement Steps 12–19 (ABM setup, calibration, scenarios).

- **Days 25–30**:  
- Baselines, ablations, visualizations, and initial paper drafting.

You can stretch this across months; the point is that the steps are modular.

---

## 5. WHAT TO ASK A CODING ASSISTANT AT EACH MILESTONE

You can copy–paste these prompts to get help from another AI when needed.

### After Preprocessing

> “I have `data/processed/ess_processed.csv` and `data/processed/lfs_processed.csv`.  
>  Here is a preview (first 20 rows).  
>  Does this look clean and reasonable for causal forest training? Anything obviously broken?”

### After Causal Forest Training

> “Here are my validation metrics for the causal forest (R², RMSE, plots).  
>  Are these good enough? Do you see any signs of overfitting or bad calibration?”

### After ABM Calibration

> “Here is my calibration report: simulated vs. actual employment and Gini.  
>  Are the errors small enough? Any advice on tuning the model further?”

### After Policy Scenarios

> “These are the scenario results (employment, inequality, emissions).  
>  Do these patterns seem interpretable and plausible for degrowth policies?”

---

## 6. MINIMUM VIABLE PRODUCT (IF TIME IS SHORT)

If you are short on time and just need something that works:

1. **Skip**: Very sophisticated baselines/ablations.
2. **Focus on**:
- One adoption outcome (e.g., work-time reduction).
- A simpler ABM:
  - Fewer sectors (e.g., 5 aggregate sectors).
  - Fewer regions (e.g., EU-level or a small subset).
3. **Still do**:
- Causal forest (even if with fewer features).
- Baseline vs. one policy scenario.
- A couple of simple, clear figures.

Even this “light” version is already more advanced than many conference submissions.

---

## 7. HOW TO KNOW YOU’RE ON TRACK

You’re on track if:

- You can explain in one sentence what the causal forest is doing.
- You can explain in one sentence what the ABM is doing.
- You can run a script that:
- Loads survey data,
- Trains a model,
- And prints adoption probabilities by income group.

Everything else (pretty plots, extra baselines) is extra polish.

---

## 8. QUICK FAQ

**Q: I don’t have the exact ESS / LFS / Exiobase files. What now?**  
A: Use any publicly available EU (or similar) micro data with policy-attitude questions and build the same pipeline; the methodology is what matters, not the exact brand name of the dataset. [web:60][web:258]

**Q: Do I need cloud compute?**  
A: No. The roadmap is designed to run on a single laptop with 16 GB RAM by using ~1M or fewer agents and reasonable model sizes.

**Q: What if causal forest is too slow?**  
A: Start with a simpler random forest or gradient-boosting model for heterogeneous adoption; later, you can upgrade to a “proper” causal forest.

---

## 9. WHAT TO DO RIGHT NOW

1. Create the project folder.
2. Create the three markdown files and paste in the content.
3. Create `src/00_setup.py` with the tiny script above.
4. Run `python src/00_setup.py` to confirm your skeleton is alive.
5. Then start on the data steps from `DEVELOPMENT_ROADMAP.md`.

Once those three files exist and you can run one Python file, you can feed all of that to Cursor or any other coding assistant and have it generate the actual implementation scripts step by step.