import pandas as pd
import numpy as np

from sklearn.inspection import permutation_importance
from sklearn.calibration import calibration_curve
from sklearn.metrics import accuracy_score, log_loss, roc_auc_score, brier_score_loss, confusion_matrix, ConfusionMatrixDisplay

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap
from mplsoccer import Pitch


def permute_compute(models, X_train, y_train, X_test):

    for name, model in models.items():
        result = permutation_importance(model, X_train, y_train, n_repeats=30, random_state=42, scoring="roc_auc")   # accuracy, log loss, or brier score

        importance = pd.DataFrame( {"Feature": X_test.columns, 
                                    "Importance": result.importances_mean}).sort_values(by="Importance", ascending=True)

        return name, importance


def plot_predictions(data, cordinates):
    pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black', linewidth=1)
    colors = ['red', 'yellow', 'green']
    cmap = LinearSegmentedColormap.from_list('my_colormap', colors)
    sc = pitch.scatter

    for name, df in data.items():
        fig = plt.figure(figsize=(18, 14), constrained_layout=True)
        gs = GridSpec(2, 1, height_ratios=[1, 1], figure=fig)

        ax_pitch = fig.add_subplot(gs[0])
        ax_hist = fig.add_subplot(gs[1])

        # ---- TOP: Pitch Plot ----
        pitch.draw(ax=ax_pitch)

        sc = pitch.scatter(cordinates['x'], cordinates['y'], c=df['xG'], cmap=cmap,
                        edgecolors='black', linewidth=0.4, s=55, vmin=0, vmax=1, ax=ax_pitch)

        ax_pitch.set_title(f'{name} xG Shot Map', fontsize=16, pad=10)

        cbar = fig.colorbar(sc, ax=ax_pitch, fraction=0.025, pad=0.02)
        cbar.set_label(f'{name} xG Probability')

        # ---- BOTTOM: Histogram ----
        ax_hist.hist(df['xG'], bins=50, edgecolor='black')

        ax_hist.set_title(f'{name} xG Distribution', fontsize=14)
        ax_hist.set_xlabel('xG')
        ax_hist.set_ylabel('Frequency')

        plt.savefig(f'{name} xG Distribution.png')
        plt.show()


def plot_calibration_curves(y_test, predictions, title):
    plt.figure(figsize=(8, 6))

    for model_name, prediction in predictions.items():
        prob_true, prob_pred = calibration_curve(
            y_test,
            prediction,
            n_bins=10
        )
        plt.plot(prob_pred, prob_true, marker="o", label=model_name)

    plt.plot([0, 1], [0, 1], linestyle="--", color="black")
    plt.xlabel("Predicted Probability")
    plt.ylabel("Observed Goal Frequency")
    plt.title(f'{title}.png')
    plt.legend()
    plt.show()


def plot_confusion_matrices(y_test, predictions, title):
    for model_name, prediction in predictions.items():
        cm = confusion_matrix(y_test, prediction)
        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm,
            display_labels=["Miss", "Goal"]
        )
        disp.plot(cmap=plt.cm.Blues)
        plt.title(f"{model_name} Confusion Matrix")
        plt.savefig(f"{model_name} Confusion Matrix.png")
        plt.show()