"""
evaluate_model.py
Generates and saves the standard ML evaluation visuals (confusion matrix,
ROC curve, feature importance) as PNG files, used in the dashboard and
the project report. Run this after random_forest_model.train_random_forest().
"""
import os
import numpy as np
import matplotlib.pyplot as plt

from ml_module.random_forest_model import train_random_forest

OUT_DIR = "ml_module/evaluation_plots"


def plot_confusion_matrix(cm, classes, save_path):
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix - Random Forest")
    thresh = np.array(cm).max() / 2
    for i in range(len(cm)):
        for j in range(len(cm[i])):
            ax.text(j, i, cm[i][j], ha="center", va="center",
                     color="white" if cm[i][j] > thresh else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_roc_curve(roc_data, save_path):
    fig, ax = plt.subplots(figsize=(5, 4))
    for cls, data in roc_data.items():
        ax.plot(data["fpr"], data["tpr"], label=f"{cls} (AUC={data['auc']})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curve (One-vs-Rest)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def plot_feature_importance(importance_dict, save_path):
    names = list(importance_dict.keys())
    values = list(importance_dict.values())
    order = np.argsort(values)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh([names[i] for i in order], [values[i] for i in order], color="#2563eb")
    ax.set_title("Feature Importance - Random Forest")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def run_full_evaluation():
    os.makedirs(OUT_DIR, exist_ok=True)
    metrics = train_random_forest()

    plot_confusion_matrix(metrics["confusion_matrix"], metrics["classes"],
                           os.path.join(OUT_DIR, "confusion_matrix.png"))
    plot_roc_curve(metrics["roc_curve"], os.path.join(OUT_DIR, "roc_curve.png"))
    plot_feature_importance(metrics["feature_importance"],
                             os.path.join(OUT_DIR, "feature_importance.png"))

    print(f"Accuracy: {metrics['accuracy']}, F1: {metrics['f1_score']}")
    print(f"Plots saved to {OUT_DIR}/")
    return metrics


if __name__ == "__main__":
    run_full_evaluation()
