"""
Preprocessing Pipeline for Smart Waste Management.
Handles data cleaning, missing value check, outlier bounds, categorical encoding,
and strict train/test scaling without data leakage.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from src.feature_engineering import add_engineered_features

def preprocess_raw_data(df: pd.DataFrame, is_training: bool = True, scaler=None, fit_scaler: bool = False):
    """
    Preprocesses raw smart bin dataset:
    - Cleans missing/duplicate records
    - Applies feature engineering
    - One-hot encodes Container Type
    - Scales numerical features using StandardScaler
    """
    df = df.copy()
    
    # Drop duplicates if any
    df = df.drop_duplicates()
    
    # Fill missing values if any
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df[col] = df[col].fillna(df[col].median())
            
    if 'Container Type' in df.columns and df['Container Type'].isnull().sum() > 0:
        df['Container Type'] = df['Container Type'].fillna('Medium')
        
    # Feature engineering
    df = add_engineered_features(df)
    
    # One-hot encoding for Container Type (Drop 'Small' as baseline)
    container_dummies = pd.get_dummies(df['Container Type'], prefix='Container Type', drop_first=False)
    for c_type in ['Container Type_Medium', 'Container Type_Large', 'Container Type_Industrial']:
        if c_type not in container_dummies.columns:
            container_dummies[c_type] = 0
            
    # Include specified dummy columns
    encoded_cols = ['Container Type_Medium', 'Container Type_Large', 'Container Type_Industrial']
    df = pd.concat([df, container_dummies[encoded_cols]], axis=1)
    
    # Define features
    feature_cols = [
        'FL_A', 'FL_B', 'FL_A_3', 'FL_B_3', 'FL_A_12', 'FL_B_12', 'VS',
        'Recyclable Fraction', 'fill_diff_A_3', 'fill_diff_B_3',
        'fill_diff_A_12', 'fill_diff_B_12', 'max_fill', 'min_fill',
        'avg_fill', 'sensor_delta', 'acc_rate_3h', 'container_vol_weight',
        'Container Type_Medium', 'Container Type_Large', 'Container Type_Industrial'
    ]
    
    X = df[feature_cols]
    y = df['Class'] if 'Class' in df.columns else None
    
    if fit_scaler or (is_training and scaler is None):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    elif scaler is not None:
        X_scaled = scaler.transform(X)
    else:
        X_scaled = X.values
        
    X_scaled_df = pd.DataFrame(X_scaled, columns=feature_cols, index=df.index)
    
    return X_scaled_df, y, scaler


def prepare_train_test_data(filepath='data/raw/Smart_Bin.csv', test_size=0.2, random_state=42):
    """
    Loads raw dataset, performs 80/20 train/test split, and fits scaler ONLY on X_train to prevent leakage.
    Returns X_train_scaled, X_test_scaled, y_train, y_test, scaler, raw_df.
    """
    raw_df = pd.read_csv(filepath)
    
    # Perform raw Train/Test Split first to enforce strict data leakage prevention
    train_raw, test_raw = train_test_split(raw_df, test_size=test_size, random_state=random_state, stratify=raw_df['Class'])
    
    # Fit scaler strictly on train_raw
    X_train_scaled, y_train, scaler = preprocess_raw_data(train_raw, is_training=True, fit_scaler=True)
    
    # Transform test_raw using fitted scaler
    X_test_scaled, y_test, _ = preprocess_raw_data(test_raw, is_training=False, scaler=scaler, fit_scaler=False)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, raw_df
