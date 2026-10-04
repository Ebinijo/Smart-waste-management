"""
Priority Scoring Index (PSI) Engine for Smart Waste Management.
Calculates a mathematical urgency score (0 - 100) combining ML predictions,
sensor fill levels, fill accumulation rates, and container capacity weights.
"""

import numpy as np
import pandas as pd

def calculate_priority_score(
    predicted_prob: float,
    fl_a: float,
    fl_b: float,
    fl_a_3: float,
    container_type: str = 'Medium',
    w1: float = 0.40,
    w2: float = 0.35,
    w3: float = 0.15,
    w4: float = 0.10
) -> dict:
    """
    Calculates Priority Scoring Index (PSI) for a single bin.
    
    Formula:
    PSI = w1 * (Prob * 100) + w2 * max(FL_A, FL_B) + w3 * (AccRate_3h * 5) + w4 * (VolWeight * 10)
    
    Returns score, risk level, and component breakdown for explainability.
    """
    max_fill = max(fl_a, fl_b)
    acc_rate_3h = max(0.0, (fl_a - fl_a_3) / 3.0) # % per hour
    
    vol_weights = {'Small': 0.6, 'Medium': 0.8, 'Large': 1.0, 'Industrial': 1.2}
    vol_w = vol_weights.get(container_type, 0.8)
    
    # Sub-scores
    ml_component = predicted_prob * 100.0
    fill_component = max_fill
    rate_component = min(100.0, acc_rate_3h * 10.0) # scaled 0-100
    vol_component = vol_w * 83.33 # scaled 0-100 (1.2 -> 100)
    
    raw_score = (w1 * ml_component) + (w2 * fill_component) + (w3 * rate_component) + (w4 * vol_component)
    final_score = float(np.clip(raw_score, 0.0, 100.0))
    
    # Category Assignment
    if final_score >= 80.0:
        priority_level = 'CRITICAL'
        recommended_action = 'Collect Immediately (Shift 1)'
    elif final_score >= 65.0:
        priority_level = 'HIGH'
        recommended_action = 'Collect Today (Shift 2)'
    elif final_score >= 45.0:
        priority_level = 'MEDIUM'
        recommended_action = 'Schedule Next Shift / Tomorrow'
    else:
        priority_level = 'LOW'
        recommended_action = 'Defer Collection; Monitor Sensor'
        
    return {
        'priority_score': round(final_score, 1),
        'priority_level': priority_level,
        'recommended_action': recommended_action,
        'breakdown': {
            'ml_prob_contrib': round(w1 * ml_component, 1),
            'fill_level_contrib': round(w2 * fill_component, 1),
            'accumulation_contrib': round(w3 * rate_component, 1),
            'capacity_contrib': round(w4 * vol_component, 1)
        }
    }


def batch_calculate_priority(df: pd.DataFrame, predicted_probs: np.ndarray) -> pd.DataFrame:
    """
    Computes priority scores and risk tiers for a batch DataFrame of bins.
    """
    df = df.copy()
    scores = []
    levels = []
    actions = []
    
    probs = predicted_probs if predicted_probs is not None else df.get('Predicted_Prob', np.zeros(len(df)))
    
    for idx, row in df.iterrows():
        p_val = probs[idx] if isinstance(probs, (list, np.ndarray, pd.Series)) else 0.5
        res = calculate_priority_score(
            predicted_prob=p_val,
            fl_a=row['FL_A'],
            fl_b=row['FL_B'],
            fl_a_3=row['FL_A_3'],
            container_type=row.get('Container Type', 'Medium')
        )
        scores.append(res['priority_score'])
        levels.append(res['priority_level'])
        actions.append(res['recommended_action'])
        
    df['Priority_Score'] = scores
    df['Priority_Level'] = levels
    df['Recommended_Action'] = actions
    
    return df
