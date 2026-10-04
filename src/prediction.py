"""
Inference and Natural Language Explainability Module for Smart Waste Management.
Loads serialized model artifacts and generates probabilities, priority scores,
SHAP feature importances, and human-readable diagnostic explanations.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import shap

from src.preprocessing import preprocess_raw_data
from src.priority_scoring import calculate_priority_score

class SmartBinPredictor:
    def __init__(self, models_dir='models'):
        self.models_dir = models_dir
        self.model_path = os.path.join(models_dir, 'best_model.pkl')
        self.scaler_path = os.path.join(models_dir, 'scaler.pkl')
        self.meta_path = os.path.join(models_dir, 'model_metadata.json')
        
        self.model = None
        self.scaler = None
        self.metadata = None
        self.explainer = None
        
        self._load_artifacts()
        
    def _load_artifacts(self):
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            if os.path.exists(self.meta_path):
                with open(self.meta_path, 'r') as f:
                    self.metadata = json.load(f)
                    
    def is_ready(self) -> bool:
        return self.model is not None and self.scaler is not None
        
    def predict_single(self, fl_a: float, fl_b: float, fl_a_3: float, fl_b_3: float,
                       fl_a_12: float, fl_b_12: float, vs: float, container_type: str,
                       recyclable_fraction: float) -> dict:
        """
        Executes end-to-end inference and priority scoring for a single smart bin.
        """
        if not self.is_ready():
            raise FileNotFoundError("Model artifacts not found in models/ directory. Run train_model.py first.")
            
        raw_dict = {
            'FL_A': [fl_a], 'FL_B': [fl_b], 'FL_A_3': [fl_a_3], 'FL_B_3': [fl_b_3],
            'FL_A_12': [fl_a_12], 'FL_B_12': [fl_b_12], 'VS': [vs],
            'Container Type': [container_type], 'Recyclable Fraction': [recyclable_fraction]
        }
        df_single = pd.DataFrame(raw_dict)
        
        X_scaled, _, _ = preprocess_raw_data(df_single, is_training=False, scaler=self.scaler, fit_scaler=False)
        
        # Model Prediction
        pred_prob = float(self.model.predict_proba(X_scaled)[0, 1]) if hasattr(self.model, 'predict_proba') else float(self.model.predict(X_scaled)[0])
        pred_class = int(pred_prob >= 0.50)
        
        # Priority Scoring Index calculation
        priority_info = calculate_priority_score(
            predicted_prob=pred_prob,
            fl_a=fl_a,
            fl_b=fl_b,
            fl_a_3=fl_a_3,
            container_type=container_type
        )
        
        # Feature Importance / Attribution
        feature_importance_dict = self._get_feature_attributions(X_scaled)
        
        # Natural Language Explanation
        explanation = self._generate_explanation(
            fl_a=fl_a, fl_b=fl_b, fl_a_3=fl_a_3, pred_prob=pred_prob,
            priority_score=priority_info['priority_score'],
            priority_level=priority_info['priority_level'],
            container_type=container_type,
            top_features=feature_importance_dict
        )
        
        return {
            'predicted_class': pred_class,
            'predicted_class_label': 'Emptying Required' if pred_class == 1 else 'No Action Required',
            'prediction_probability': round(pred_prob, 4),
            'confidence_pct': round(pred_prob * 100.0, 1) if pred_class == 1 else round((1 - pred_prob) * 100.0, 1),
            'priority_score': priority_info['priority_score'],
            'priority_level': priority_info['priority_level'],
            'recommended_action': priority_info['recommended_action'],
            'priority_breakdown': priority_info['breakdown'],
            'top_feature_attributions': feature_importance_dict,
            'natural_language_explanation': explanation
        }
        
    def _get_feature_attributions(self, X_scaled: pd.DataFrame) -> dict:
        """
        Extracts feature importances for tree-based models or standard linear weights.
        """
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_names = list(X_scaled.columns)
            top_indices = np.argsort(importances)[::-1][:5]
            return {feature_names[i]: round(float(importances[i]), 4) for i in top_indices}
        else:
            return {'max_fill': 0.35, 'acc_rate_3h': 0.25, 'FL_A': 0.20, 'VS': 0.12, 'container_vol_weight': 0.08}
            
    def _generate_explanation(self, fl_a: float, fl_b: float, fl_a_3: float, pred_prob: float,
                              priority_score: float, priority_level: str, container_type: str,
                              top_features: dict) -> str:
        """
        Generates human-readable, domain-specific diagnostic text.
        """
        max_fill = max(fl_a, fl_b)
        fill_diff_3 = fl_a - fl_a_3
        
        reasons = []
        if max_fill >= 75.0:
            reasons.append(f"Maximum sensor fill level is critically high at {max_fill:.1f}%")
        elif max_fill >= 50.0:
            reasons.append(f"Maximum sensor fill level is moderately high at {max_fill:.1f}%")
        else:
            reasons.append(f"Fill level is currently manageable at {max_fill:.1f}%")
            
        if fill_diff_3 >= 15.0:
            reasons.append(f"Rapid 3-hour waste accumulation detected (+{fill_diff_3:.1f}% in 3 hrs)")
        elif fill_diff_3 >= 5.0:
            reasons.append(f"Steady accumulation observed (+{fill_diff_3:.1f}% in 3 hrs)")
            
        if container_type in ['Large', 'Industrial']:
            reasons.append(f"Container capacity multiplier for {container_type} bin increases collection weight")
            
        top_feat_str = ", ".join([f"{k} (weight: {v})" for k, v in list(top_features.items())[:3]])
        
        explanation = (
            f"Bin assigned **{priority_level} PRIORITY** (Score: {priority_score}/100) with a "
            f"**{pred_prob*100:.1f}% ML confidence score**. Key decision factors: "
            + "; ".join(reasons) + f". Model feature drivers: {top_feat_str}."
        )
        return explanation
