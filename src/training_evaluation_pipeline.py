import subprocess

def install_from_file(file_path="/Users/nanakwamekankam/Desktop/Football_Stats/xG/Scripts/requirements.txt"):
    command = ["conda", "install", "-y", "--file", file_path]
    subprocess.check_call(command)
    # Executes: conda install -y --file requirements.txt


install_from_file()

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import log_loss, roc_auc_score, brier_score_loss, accuracy_score, confusion_matrix
import xgboost as xgb
from catboost import CatBoostClassifier
from tabpfn_client import TabPFNClassifier, set_access_token
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.calibration import calibration_curve
import numpy as np
from matplotlib.gridspec import GridSpec


def train(X_train, y_train, X_test, y_test):
    # # DATA parsing
    # text = "Data Parsing"
    # print(f"{text.center()}")
    # print("---------------------------------------------------------------------------")
    # y = df['goal']
    # X = df.drop(['goal', 'shot_statsbomb_xg', 'location', 'player_x', 'player_id', 'position'], axis=1)
    # text = "Data Parsed 100/100"
    # print(f"{text.center()}")
    # print("---------------------------------------------------------------------------")

    # if X.shape[0] != y.shape[0]:
    #     print(f"{X.shape}, {y.shape}") 
    #     raise Exception("lengths X and Y are not")

    # # TRAIN/TEST SPLIT
    # print("---------------------------------------------------------------------------")
    # text = "Spliting Data"
    # print(f"{text.center()}")
    # print("---------------------------------------------------------------------------")

    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    cordinates = X_test[['x', 'y']] # for model visualizations
    # X_train.drop(["x", "y"], axis=1, inplace=True)
    # X_test.drop(["x", "y"], axis=1, inplace=True)

    # text = "Train/Test Split established"
    # print(f"{text.center()}")
    # print("---------------------------------------------------------------------------")

    # MODELING
    # LOGISTIC REGRESSION
    text = "Logistic Regression"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    logistic_regressor = LogisticRegression(max_iter=1000)
    logistic_regressor.fit(X_train, y_train)

    y_log= logistic_regressor.predict_proba(X_test)[:,1]
    goal_log = logistic_regressor.predict(X_test)

    log_df = X_test.copy()
    log_df['xG'] = y_log

    print("---------------------------------------------------------------------------")
    text = "Logistic Regression Complete 100/100"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    # RANDOM FORESTING
    text = "Random Forest"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    random_forest = RandomForestClassifier(
    n_estimators=500,
    max_depth=8,
    min_samples_split=20,
    min_samples_leaf=10,
    # class_weight='balanced_subsample',
    max_features='sqrt',
    bootstrap=True,
    random_state=42,
    n_jobs=-1
    )
    # try tuning parameters
    random_forest.fit(X_train, y_train)
    y_rf = random_forest.predict_proba(X_test)[:,1]
    goal_rf = random_forest.predict(X_test)

    rf_df = pd.DataFrame()
    rf_df['Goal'] = y_test.copy()
    rf_df['xG'] = y_rf

    print("---------------------------------------------------------------------------")
    text = "Random Forest Complete 100/100"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    # XGBOOST
    text = "XGBoosdt"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    xgb = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    objective='binary:logistic'
    )

    xgb.fit(X_train, y_train)
    y_xgb = xgb.predict_proba(X_test)[:,1]
    goal_xgb = xgb.predict(X_test)

    xgb_df = pd.DataFrame()
    xgb_df['Goal'] = y_test.copy()
    xgb_df['xG'] = y_rf

    print("---------------------------------------------------------------------------")
    text = "XGBoost Complete 100/100"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    # CATBOOST
    text = "CatBoost"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    catBoost = CatBoostClassifier(
    iterations=100,
    learning_rate=0.1,
    depth=6,
    verbose=10
    )

    catBoost.fit(X_train, y_train)
    y_cat = catBoost.predict_proba(X_test)[:,1]
    goal_cat = catBoost.predict(X_test)
    cat_df = pd.DataFrame()
    cat_df['Goal'] = y_test.copy()
    cat_df['xG'] = y_cat

    print("---------------------------------------------------------------------------")
    text = "CatBoost Complete 100/100"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    # TabFPN
    text = "Foundational Model Approach(TabFPN)"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    print("To use tabpfn:\n1. Open https://ux.priorlabs.ai in a browser and log in (or register)\n2. Accept the license on the Licenses tab\n3. Copy your API Key from https://ux.priorlabs.ai/account\n4. Set the environment variable: export TABPFN_TOKEN='<your-api-key>'")

    api_key = input("Input your api-key here: ")
    set_access_token(api_key)
    tabPFN = TabPFNClassifier()
    tabPFN.fit(X_train, y_train)
    goal_tabPFN = tabPFN.predict(X_test)
    y_tabPFN = tabPFN.predict_proba(X_test)[:,1]

    print("---------------------------------------------------------------------------")
    text = "TabPFN Complete 100/100"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    return cordinates, y_log, goal_log, y_rf, goal_rf, y_xgb, goal_xgb, y_cat, goal_cat, y_tabPFN, goal_tabPFN


def evaluation(y_test, goal_log, y_log, goal_rf, y_rf, goal_xgb, y_xgb, goal_cat, y_cat, y_tabPFN, goal_tabPFN):
    text = "MODEL EVALUATION..."
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")

    text = "Logistic Regression"
    print(f"{text.center()}")
    print(f"Accuracy: {accuracy_score(y_test, goal_log):.3f}\nLog Loss: {log_loss(y_test, y_log):.3f}\nROC_AUC Score: {roc_auc_score(y_test, y_log):.3f}\nBrier Score: {brier_score_loss(y_test, y_log):.3f}")
    print("---------------------------------------------------------------------------")

    text = "Random Forest"
    print(f"{text.center()}")
    print(f"Accuracy: {accuracy_score(y_test, goal_rf):.3f}\nLog Loss: {log_loss(y_test, y_rf):.3f}\nROC_AUC Score: {roc_auc_score(y_test, y_rf):.3f}\nBrier Score: {brier_score_loss(y_test, y_rf):.3f}")
    print("---------------------------------------------------------------------------")

    text = "XGBoost"
    print(f"{text.center()}")
    print(f"Accuracy: {accuracy_score(y_test, goal_xgb):.3f}\nLog Loss: {log_loss(y_test, y_xgb):.3f}\nROC_AUC Score: {roc_auc_score(y_test, y_xgb):.3f}\nBrier Score: {brier_score_loss(y_test, y_xgb):.3f}")
    print("---------------------------------------------------------------------------")

    text = "CatBoost"
    print(f"{text.center()}")
    print(f"Accuracy: {accuracy_score(y_test, goal_cat):.3f}\nLog Loss: {log_loss(y_test, y_cat):.3f}\nROC_AUC Score: {roc_auc_score(y_test, y_cat):.3f}\nBrier Score: {brier_score_loss(y_test, y_cat):.3f}")
    print("---------------------------------------------------------------------------")

    text = "TabPFN"
    print(f"{text.center()}")
    print(f"Accuracy: {accuracy_score(y_test, goal_tabPFN):.3f}\nLog Loss: {log_loss(y_test, y_tabPFN):.3f}\nROC_AUC Score: {roc_auc_score(y_test, y_tabPFN):.3f}\nBrier Score: {brier_score_loss(y_test, y_tabPFN):.3f}")
    print("---------------------------------------------------------------------------")


    text = "Confusion Matrices"
    print(f"{text.center()}")
    print("---------------------------------------------------------------------------")
    goal_dataframes = {"Logistic Regression": goal_log,
                   "Random Forest": goal_rf,
                   "XGBoost": goal_xgb,
                   "CatBoost": goal_cat}

    for key, value in goal_dataframes.items():
        cm = confusion_matrix(y_test, value)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Miss', 'Score'])
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"{key} Confusion Matrix")
        plt.show()
    
    print("---------------------------------------------------------------------------")

    # # Feature Importance
    # text = "Feature Importance"
    # print(f"{text.center()}")
    # print("---------------------------------------------------------------------------")
    # models = [random_forest, xgboost, catboost]
    # for model in models:
    #     importance = pd.Series(model.feature_importances_,index=model.columns).sort_values(ascending=False)

    # print(importance)

    model_predictors = {
    'Logistic Regression': y_log,
    'Random Forest': y_rf,
    'XGBoost': y_xgb,
    'CatBoost': y_cat,
    'TabPFN': y_tabPFN
    }

    for name, y_model in model_predictors.items():
        prob_rf, prob_pred = calibration_curve(y_test, y_model, n_bins=10)

        plt.plot(prob_pred, prob_rf, marker='o')
        plt.plot([0,1], [0,1], linestyle='--')

        plt.xlabel("Predicted Probability")
        plt.ylabel("Observed Frequency")
        plt.title(f"{name} Calibration")
        plt.show()



if __name__ == "__main__":
    train()