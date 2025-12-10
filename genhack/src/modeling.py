"""
Phase 2: Modeling - Residual Learning for Temperature Downscaling
Implements spatial cross-validation and model training
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from pathlib import Path
from typing import Tuple, Dict, List, Optional
import matplotlib.pyplot as plt
import seaborn as sns


class SpatialCrossValidator:
    """Implement spatial cross-validation to prevent data leakage"""
    
    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state
    
    def spatial_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data by station location (not by time)
        This ensures the model can generalize to unseen locations
        
        Args:
            df: Training dataframe with STAID column
        
        Returns:
            train_df, test_df
        """
        # Get unique stations
        unique_stations = df['STAID'].unique()
        
        # Split stations (not individual observations)
        train_stations, test_stations = train_test_split(
            unique_stations,
            test_size=self.test_size,
            random_state=self.random_state
        )
        
        # Create train/test splits
        train_df = df[df['STAID'].isin(train_stations)].copy()
        test_df = df[df['STAID'].isin(test_stations)].copy()
        
        print(f"Spatial split:")
        print(f"  Train: {len(train_stations)} stations, {len(train_df)} samples")
        print(f"  Test: {len(test_stations)} stations, {len(test_df)} samples")
        
        return train_df, test_df
    
    def geographic_split(self, df: pd.DataFrame, 
                        split_type: str = 'latitude') -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data geographically (e.g., North/South or East/West)
        
        Args:
            df: Training dataframe
            split_type: 'latitude' (North/South) or 'longitude' (East/West)
        
        Returns:
            train_df, test_df
        """
        if split_type == 'latitude':
            # Calculate median latitude
            median_coord = df['LAT'].median()
            coord_col = 'LAT'
        else:
            # Calculate median longitude
            median_coord = df['LON'].median()
            coord_col = 'LON'
        
        # Split by median
        train_df = df[df[coord_col] <= median_coord].copy()
        test_df = df[df[coord_col] > median_coord].copy()
        
        print(f"Geographic split ({split_type}):")
        print(f"  Train: {len(train_df)} samples ({coord_col} <= {median_coord:.2f})")
        print(f"  Test: {len(test_df)} samples ({coord_col} > {median_coord:.2f})")
        
        return train_df, test_df


class ResidualLearningModel:
    """
    Residual learning model for temperature downscaling
    
    Formula: HighRes Temp = ERA5 (9km) + Model(NDVI, Elevation, Coords)
    """
    
    def __init__(self, model_type: str = 'random_forest', **model_params):
        """
        Initialize model
        
        Args:
            model_type: Type of model ('random_forest' or 'xgboost')
            **model_params: Parameters to pass to the model
        """
        self.model_type = model_type
        self.model_params = model_params
        self.model = None
        self.feature_names = None
        self.scaler = None
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Prepare features and target for training
        
        Features: [ERA5_Temp, NDVI, Elevation, Lat, Lon, DayOfYear]
        Target: Residual (Station_Temp - ERA5_Temp)
        
        Args:
            df: Training dataframe
        
        Returns:
            X (features), y (target or None if 'Residual' not in df)
        """
        self.feature_names = ['ERA5_Temp', 'NDVI', 'ELEVATION', 'LAT', 'LON', 'DayOfYear']
        
        X = df[self.feature_names].values
        y = df['Residual'].values if 'Residual' in df.columns else None
        
        return X, y
    
    def train(self, train_df: pd.DataFrame):
        """
        Train the residual learning model
        
        Args:
            train_df: Training dataframe
        """
        X_train, y_train = self.prepare_features(train_df)
        
        print(f"\nTraining {self.model_type} model...")
        print(f"Features: {self.feature_names}")
        print(f"Training samples: {len(X_train)}")
        
        if self.model_type == 'random_forest':
            # Default parameters optimized for this task
            default_params = {
                'n_estimators': 200,
                'max_depth': 15,
                'min_samples_split': 10,
                'min_samples_leaf': 5,
                'n_jobs': -1,
                'random_state': 42,
                'verbose': 1
            }
            default_params.update(self.model_params)
            
            self.model = RandomForestRegressor(**default_params)
        
        elif self.model_type == 'xgboost':
            try:
                import xgboost as xgb
                default_params = {
                    'n_estimators': 200,
                    'max_depth': 8,
                    'learning_rate': 0.1,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'n_jobs': -1,
                    'random_state': 42
                }
                default_params.update(self.model_params)
                
                self.model = xgb.XGBRegressor(**default_params)
            except ImportError:
                print("XGBoost not installed, falling back to Random Forest")
                self.model = RandomForestRegressor(n_estimators=200, n_jobs=-1)
        
        # Train
        self.model.fit(X_train, y_train)
        print("Training complete!")
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict residuals for given data
        
        Args:
            df: Dataframe with feature columns
        
        Returns:
            Predicted residuals
        """
        X, _ = self.prepare_features(df)
        return self.model.predict(X)
    
    def evaluate(self, test_df: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            test_df: Test dataframe
        
        Returns:
            Dictionary of metrics
        """
        y_true = test_df['Residual'].values
        y_pred = self.predict(test_df)
        
        # Calculate metrics
        metrics = {
            'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
            'MAE': mean_absolute_error(y_true, y_pred),
            'R2': r2_score(y_true, y_pred)
        }
        
        # Also evaluate the full temperature prediction
        # HighRes Temp = ERA5 + Predicted Residual
        temp_pred = test_df['ERA5_Temp'].values + y_pred
        temp_true = test_df['Station_Temp'].values
        
        # Compare to baseline (ERA5 alone)
        era5_baseline = test_df['ERA5_Temp'].values
        
        metrics['Temp_RMSE'] = np.sqrt(mean_squared_error(temp_true, temp_pred))
        metrics['Temp_MAE'] = mean_absolute_error(temp_true, temp_pred)
        metrics['Baseline_RMSE'] = np.sqrt(mean_squared_error(temp_true, era5_baseline))
        metrics['Baseline_MAE'] = mean_absolute_error(temp_true, era5_baseline)
        metrics['Improvement_RMSE'] = metrics['Baseline_RMSE'] - metrics['Temp_RMSE']
        
        return metrics
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from trained model
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if self.model is None:
            return pd.DataFrame()
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            
            df = pd.DataFrame({
                'Feature': self.feature_names,
                'Importance': importance
            })
            df = df.sort_values('Importance', ascending=False)
            
            return df
        else:
            return pd.DataFrame()
    
    def save(self, filepath: str):
        """Save trained model to disk"""
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, filepath)
        print(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str):
        """Load trained model from disk"""
        data = joblib.load(filepath)
        
        instance = cls(model_type=data['model_type'])
        instance.model = data['model']
        instance.feature_names = data['feature_names']
        
        return instance


def train_and_evaluate_model(training_data: pd.DataFrame,
                             split_type: str = 'spatial',
                             model_type: str = 'random_forest',
                             output_dir: str = None) -> Tuple[ResidualLearningModel, Dict]:
    """
    Complete training and evaluation pipeline
    
    Args:
        training_data: Prepared training dataframe
        split_type: 'spatial' or 'geographic'
        model_type: 'random_forest' or 'xgboost'
        output_dir: Directory to save outputs
    
    Returns:
        Trained model and evaluation metrics
    """
    print("\n=== Phase 2: Model Training ===")
    
    # Step 1: Create spatial split
    print("\n--- Step 1: Creating Train/Test Split ---")
    splitter = SpatialCrossValidator(test_size=0.2)
    
    if split_type == 'spatial':
        train_df, test_df = splitter.spatial_split(training_data)
    else:
        train_df, test_df = splitter.geographic_split(training_data)
    
    # Step 2: Train model
    print("\n--- Step 2: Training Model ---")
    model = ResidualLearningModel(model_type=model_type)
    model.train(train_df)
    
    # Step 3: Evaluate
    print("\n--- Step 3: Evaluation ---")
    metrics = model.evaluate(test_df)
    
    print("\n=== Evaluation Results ===")
    print(f"Residual Prediction:")
    print(f"  RMSE: {metrics['RMSE']:.3f}°C")
    print(f"  MAE:  {metrics['MAE']:.3f}°C")
    print(f"  R²:   {metrics['R2']:.3f}")
    print(f"\nFull Temperature Prediction:")
    print(f"  Model RMSE:    {metrics['Temp_RMSE']:.3f}°C")
    print(f"  Baseline RMSE: {metrics['Baseline_RMSE']:.3f}°C")
    print(f"  Improvement:   {metrics['Improvement_RMSE']:.3f}°C")
    
    # Feature importance
    print("\n=== Feature Importance ===")
    importance = model.get_feature_importance()
    print(importance.to_string(index=False))
    
    # Save outputs
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model.save(output_path / 'residual_model.pkl')
        
        # Save metrics
        metrics_df = pd.DataFrame([metrics])
        metrics_df.to_csv(output_path / 'evaluation_metrics.csv', index=False)
        
        # Save feature importance
        importance.to_csv(output_path / 'feature_importance.csv', index=False)
        
        # Save test predictions for analysis
        test_df_copy = test_df.copy()
        test_df_copy['Predicted_Residual'] = model.predict(test_df)
        test_df_copy['Predicted_Temp'] = test_df_copy['ERA5_Temp'] + test_df_copy['Predicted_Residual']
        test_df_copy.to_csv(output_path / 'test_predictions.csv', index=False)
        
        print(f"\nOutputs saved to {output_dir}")
    
    return model, metrics


if __name__ == "__main__":
    # Example usage
    import sys
    
    # Load training data
    training_data = pd.read_csv('../outputs/training_data.csv')
    training_data['DATE'] = pd.to_datetime(training_data['DATE'])
    
    # Train and evaluate
    model, metrics = train_and_evaluate_model(
        training_data,
        split_type='spatial',
        model_type='random_forest',
        output_dir='../outputs'
    )
