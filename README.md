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
├── data/
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
│
├── requirements.txt
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
*** Events distilled down to shots.***
*** Came to ~9900 rows, might need more data***
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
- XGBoost (planned)

Evaluation metrics:

- Log Loss
- ROC-AUC
- Brier Score
- Calibration
- Accuracy
---

## Stage 5 - xG for shot context

This model includes the features from baseline the baseline model and features giving shot context.
These include:

- Aerial
- First time 
- Pressure
- Open goal
- Follows dribble
- Body part
- Shot technique
---

## Stage 4 — Player Ability Integration(In progress...)

Following the shot context, it makes sense to investigate the player's scoring ability.

The work in this stage focuses on integrating external player ratings from SoFIFA.
Two models are developed:
    - Model C investigates the effect of a player's scoring ability(without context) in predicting xG. This means the baseline model with the player's ability.
    - Model C(b) investigates the effect of a player's scoring ability(with context) in predicting xG. Incorporating shot technique features along side player's scoring ability.
    Model D investigates the player's ability based on the body part used. This incorporates the player's body part used in conjunction with their ability using that body part
    

Features include:

- Finishing
- Shot Power
- Long Shots
- Positioning
- Penalties
- Heading
- Preferred Foot

Custom scraping tools are being developed to automatically collect ratings across FIFA versions.
---

## Stage 5 — Goalkeeper saving Ability

In this stage, we will look at the level of opposition(goalkeeper and team defense) that the goals were scored against. 
We want to find xG by the player's scoring abaility vs the opposition's defensive ability.

Goalkeeper features include:

- Diving
- Reflexes
- Handling
- Positioning

Team defense include:
- Number of defenders in line up(based on formation)
- Avarage defensive rating of each player
- Team defensive rating

Model E will try to improve xG by simply adding the goalkeeper scoring rating and then improved by incorporating
player vs goalkeeper elo rating

---

# Technologies Used

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
5. Player and Goalkeeper Ability

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

---

# Extensions and Future Work

- Team defense(Goalkeeper ability, Overall team defensive rating, closest 3 players to ball's defensive rating(including goalkeeper), average distance from defenders to player scoring)
- Hyperparameter optimization
- Computer Vision(basic computer vision model, establishing number(and quality) of paths to goal from where shot is taken)

---

# License

This project is intended for research and educational purposes.

StatsBomb Open Data is provided under its own license.

If you run this notebook, please send me an email at nanakwameboakyekankam@gmail.com with any additions, criticisms, ideas, suggestions and findings(amongst others)

---

# Notes
Convidence or uncertainty intervals
Simplify features