"""
Model Training and Cross-Validation Pipeline for Smart Waste Management.
Compares 6 classifiers: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, LightGBM.
Performs 5-Fold Stratified Cross-Validation, hyperparameter tuning, model evaluation, and artifact serialization.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from src.preprocessing import prepare_train_test_data

def train_and_compare_models(filepath='data/raw/Smart_Bin.csv', models_dir='models'):
    """
    Executes full ML training pipeline:
    1. Loads dataset and splits 80/20 train/test with strict data leakage prevention.
    2. Runs 5-Fold Stratified CV across 6 candidate models.
    3. Selects best model, tunes hyperparameters.
    4. Evaluates on test set and saves best model artifacts.
    """
    os.makedirs(models_dir, exist_ok=True)
    
    print("Pre-processing dataset and splitting 80/20 train/test...")
    X_train, X_test, y_train, y_test, scaler, raw_df = prepare_train_test_data(filepath)
    
    # Save fitted scaler artifact
    joblib.dump(scaler, os.path.join(models_dir, 'scaler.pkl'))
    print(f"Saved fitted StandardScaler to {os.path.join(models_dir, 'scaler.pkl')}")
    
    # Define candidate models
    candidate_models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42, max_depth=8),
        'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100, max_depth=12),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42, n_estimators=100, learning_rate=0.1),
        'XGBoost': XGBClassifier(random_state=42, n_estimators=100, eval_metric='logloss'),
        'LightGBM': LGBMClassifier(random_state=42, n_estimators=100, verbose=-1)
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_results = []
    
    print("\n--- Running 5-Fold Stratified Cross-Validation ---")
    for name, model in candidate_models.items():
        scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        scores = cross_validate(model, X_train, y_train, cv=skf, scoring=scoring, n_jobs=-1)
        
        acc_mean = scores['test_accuracy'].mean()
        prec_mean = scores['test_precision'].mean()
        rec_mean = scores['test_recall'].mean()
        f1_mean = scores['test_f1'].mean()
        auc_mean = scores['test_roc_auc'].mean()
        
        cv_results.append({
            'Model': name,
            'Accuracy': round(acc_mean, 4),
            'Precision': round(prec_mean, 4),
            'Recall': round(rec_mean, 4),
            'F1-Score': round(f1_mean, 4),
            'ROC-AUC': round(auc_mean, 4)
        })
        print(f"[{name}] -> Accuracy: {acc_mean:.4f} | F1: {f1_mean:.4f} | AUC: {auc_mean:.4f}")
        
    results_df = pd.DataFrame(cv_results).sort_values(by='F1-Score', ascending=False).reset_index(drop=True)
    
    # Select best model based on F1-Score
    best_model_name = results_df.iloc[0]['Model']
    print(f"\nBest performing model selected by CV F1-Score: {best_model_name}")
    
    # Hyperparameter tuning for best model
    print(f"Tuning hyperparameters for {best_model_name}...")
    if best_model_name == 'XGBoost':
        param_grid = {
            'n_estimators': [100, 150],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1]
        }
        base_estimator = XGBClassifier(random_state=42, eval_metric='logloss')
    elif best_model_name == 'Random Forest':
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 15],
            'min_samples_split': [2, 5]
        }
        base_estimator = RandomForestClassifier(random_state=42)
    elif best_model_name == 'LightGBM':
        param_grid = {
            'n_estimators': [100, 150],
            'max_depth': [4, 6, 8],
            'learning_rate': [0.05, 0.1]
        }
        base_estimator = LGBMClassifier(random_state=42, verbose=-1)
    else:
        param_grid = {
            'n_estimators': [100, 150],
            'max_depth': [4, 6],
            'learning_rate': [0.05, 0.1]
        }
        base_estimator = GradientBoostingClassifier(random_state=42)
        
    grid_search = GridSearchCV(base_estimator, param_grid, cv=skf, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    final_model = grid_search.best_estimator_
    print(f"Best Hyperparameters: {grid_search.best_params_}")
    
    # Evaluate final tuned model on held-out Test set
    y_pred = final_model.predict(X_test)
    y_prob = final_model.predict_proba(X_test)[:, 1] if hasattr(final_model, 'predict_proba') else y_pred
    
    test_accuracy = accuracy_score(y_test, y_pred)
    test_precision = precision_score(y_test, y_pred)
    test_recall = recall_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("\n================ FINAL TEST SET EVALUATION ================")
    print(f"Test Accuracy:  {test_accuracy:.4f}")
    print(f"Test Precision: {test_precision:.4f}")
    print(f"Test Recall:    {test_recall:.4f}")
    print(f"Test F1-Score:  {test_f1:.4f}")
    print(f"Test ROC-AUC:   {test_auc:.4f}")
    print("Confusion Matrix:")
    print(np.array(cm))
    print("==========================================================")
    
    # Save final model artifact
    joblib.dump(final_model, os.path.join(models_dir, 'best_model.pkl'))
    
    # Save metadata JSON
    metadata = {
        'model_name': best_model_name,
        'hyperparameters': grid_search.best_params_,
        'features': list(X_train.columns),
        'metrics': {
            'test_accuracy': round(float(test_accuracy), 4),
            'test_precision': round(float(test_precision), 4),
            'test_recall': round(float(test_recall), 4),
            'test_f1': round(float(test_f1), 4),
            'test_auc': round(float(test_auc), 4),
            'confusion_matrix': cm
        },
        'comparison': cv_results
    }
    
    with open(os.path.join(models_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Successfully saved trained model and metadata to '{models_dir}/'")
    return final_model, metadata, results_df


if __name__ == '__main__':
    train_and_compare_models()
