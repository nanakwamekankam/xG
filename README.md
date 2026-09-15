# xG Model Project

## Setup

Create the conda environment:

```bashgit add README.md
conda env create -f environment.yml
```

Activate it:
``` bash
conda activate xg_env
```
---
## To use tabpfn:

1. Open https://ux.priorlabs.ai in a browser and log in (or register)
2. Accept the license on the Licenses tab
3. Copy your API Key from https://ux.priorlabs.ai/account
4. Set the environment variable: export TABPFN_TOKEN="<your-api-key>"
 or in Python (before calling .fit()): import os; os.environ["TABPFN_TOKEN"] = "<your-api-key>"

---
# Expected Goals (xG) Modeling and Feature Engineering

An end-to-end football analytics project investigating whether player scoring ability coupled with goalkeeper saving ability and contextual match information improve Expected Goals (xG) prediction beyond traditional geometric shot features.

This project builds an xG model from publicly available StatsBomb event data and progressively incorporates richer contextual information—including player scoring ratings, and goalkeeper ratings to evaluate their contribution to predictive performance.

---

## Project Motivation

Most publicly available xG models rely primarily on shot location and a handful of contextual variables.

This project asks a broader research question:

> **Can incorporating player ability and contextual information significantly improve Expected Goals prediction compared to traditional geometric models?**

To answer this, the project develops multiple generations of xG models, beginning with a simple baseline before progressively introducing richer football-specific features.

---

## Research Objectives

The project investigates the predictive value of:

- Shot distance
- Shot angle
- Body part used
- Open play vs set pieces
- Shot technique
- Player finishing ability
- Goalkeeper ability
- Player recent form

Performance is evaluated using multiple machine learning models and appropriate probabilistic metrics.

---

# Dataset

This project uses publicly available **StatsBomb Open Data**.

The raw event data is **not stored in this repository** because of GitHub's file size limitations.

Instead, the first notebook automatically downloads and prepares the dataset.

---

# Repository Structure

```text
xG/
│
├── datasets/
│   ├── raw/
│   └── processed/
│
├── Notebooks/
│   ├── Stage 1 - Event Data Collection.ipynb
│   ├── Stage 2 - Data Preprocessing.ipynb
│   ├── Stage 3 - Baseline Modeling xG.ipynb
│   ├── Player and Goalkeeper ability.ipynb
│   └── ...
│
├── src/
│
├── models/
│   ├── Baseline Models
│   ├── xG_B: Baseline xG with shot context
│   ├── xG_C: Baseline xG with player scoring
│   ├── xG_D: Basleine xG with shot context and player scoring
│   
├── results/
│   ├── Baseline Models
│   ├── xG_B
│   ├── ...
│
├── requirements.txt
├── environment.yml
├── README.md
└── .gitignore
```

---

# Pipeline

## Stage 1 — Data Collection

- Download StatsBomb Open Data
- Extract shot events
- Collect match metadata
- Generate raw datasets

Output:

```
data/raw/
```

---

## Stage 2 — Data Preprocessing

Feature engineering including:

- Shot distance
- Shot angle
- Body part encoding
- Shot type
- Play pattern
- One-hot encoding
- Missing value handling

Output:

```
data/processed/
```
*** Events distilled down to shots, which comes to ~36,000 rows***
---

## Stage 3 — Baseline xG Model

The baseline features include:

- Distance
- Angle
- Shot type

Models evaluated include:

- Logistic Regression
- Random Forest
- CatBoost
- XGBoost
- TabPFN

Evaluation metrics:

- Log Loss
- ROC-AUC
- Brier Score
- Calibration Curve
- Accuracy
---

## Stage 5 - xG for shot context

This model includes the features from the baseline model and features giving shot context.
These include:

- Aerial contest
- First time 
- Pressure
- Open goal
- Follows dribble
- Body part
- Shot technique
---

## Stage 4 — Player Ability Integration

Following the shot context, it makes sense to investigate the player's scoring ability.

The work in this stage focuses on integrating external player ratings from SoFIFA.
Two models are developed:
    - Model C investigates the effect of a player's scoring ability(without context) in predicting xG. This means the baseline model with the player's ability.
    - Model D investigates the effect of a player's scoring ability(with context) in predicting xG. Incorporating shot technique features along side player's scoring ability.
    
Scoring features include:

- Finishing
- Shot Power
- Long Shots
- Positioning
- Penalties
- Volleys

---
## Stage 5 - Model Comparison and Uncertainty Analysis(In Progress...)

Bootstrap held-out test predictions. Then bootstrap the same test-shot indices and calculate:
- Log Loss — primary
- Brier Score — primary
- ROC-AUC — useful secondary metric

Here, accuracy isn't particularly useful for xG because goals are highly imbalanced and xG is fundamentally a probability model.
Then for every bootstrap sample, calculate both models on the same sampled shots. i.e. delta_logloss = logloss_D - logloss_B(negetive value shows D is better than B)

| Comparison | Question                                                    | Importance                                   |
| ---------- | ----------------------------------------------------------- | -------------------------------------------- |
| A → B      | Does shot context improve geometric xG?                     | Supporting                                   |
| B → C      | Does player scoring ability add information beyond context? | **Primary**                                  |
| C → D      | Does your final player-ability formulation improve on C?    | **Primary/secondary depending on current D** |
| A → D      | How much better is the complete model than baseline?        | Summary                                      |

---
## Project Summary

Model A establishes geometric baseline → Model B establishes value of shot circumstances → Models C/D introduce player-specific scoring ability → paired bootstrap analysis tests whether that added ability produces a reliable improvement beyond context.
---

# Modules Used

### Data Collection

- StatsBomb Open Data
- pandas
- requests
- Playwright
- BeautifulSoup
- Selenium

### Data Processing

- NumPy
- pandas
- scikit-learn

### Machine Learning

- Logistic Regression
- Random Forest
- CatBoost
- XGBoost
- TabPFN

### Visualization

- matplotlib
- mplsoccer

---

# Installation

Clone the repository

```bash
git clone https://github.com/nanakwamekankam/xG.git
cd xG
```

Create a virtual environment

```bash
conda create -n xg_env python=3.10
conda activate xg_env
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Project

Execute the notebooks in order:

1. Event Data Collection
2. Data Preprocessing
3. Baseline Modeling
4. Shot Context Analysis
5. Player Attributes
6. Shot Context with Player scoring ability analysis

The first notebook automatically downloads and prepares the required event data.

---

# Current Status

✅ Event data collection

✅ Baseline feature selection

✅ Model A: Baseline xG model

✅ Model B: xG_shot_context

✅ Feature engineering: SoFIFA player rating, preferred foot integration

✅ Model C: xG_player_abilty

✅ Model D: xG_player_ability_with_shot_context

[ ] Model Comparison and Uncertainty Analysis (In progress...)

---

# Extensions and Future Work

- Hyperparameter optimization
- Team defense(Goalkeeper ability, Overall team defensive rating, closest 3 players to ball's defensive rating(including goalkeeper), average distance from defenders to player scoring)

## Stage 5 — Resitance Analysis

In this stage, we will look at the level of opposition(goalkeeper and team defense) that the goals were scored against. 
We want to find xG by the player's scoring abaility vs the opposition's defensive ability.

Goalkeeper features include:

- Diving
- Reflexes
- Handling
- Positioning

Team defense include:
- Number of defenders in line up
- Avarage defensive rating of each player
- Team defensive rating

Model E will try to improve xG by simply adding the goalkeeper scoring rating
Then subsequent models will be developed incorporating other defensive statistics


## Stage 6 - Computer Vision Analysis

 In this stage, we will use photographic data to predict xG. 
 I would be particularly interested in building:
- A basic computer vision model,
- A methodology to:
                    1. find number of paths to goal from where shot is taken
                    2. The quality of the paths(i.e interference on the path)

---

# License

This project is intended for research and educational purposes.

StatsBomb Open Data is provided under its own license.

If you run this notebook, please send me an email at nanakwameboakyekankam@gmail.com with any additions, criticisms, ideas, suggestions and findings(amongst others)
