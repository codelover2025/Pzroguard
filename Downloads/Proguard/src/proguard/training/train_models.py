import os
import pandas as pd
import numpy as np
import joblib
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold, train_test_split, GridSearchCV
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, f1_score
from data_generator import SyntheticDataGenerator

# Optional: Disable TF logs for clean output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

OUTPUT_DIR = "src/proguard/models/trained"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ProGuardModelTrainer:
    """
    Trains Production-Grade ML Models for the ProGuard Dashboard.
    Uses Cross-Validation, SMOTE, and Hyperparameter Tuning.
    """
    def __init__(self, data_dir="src/proguard/data/synthetic"):
        self.data_dir = data_dir
        self.scaler = StandardScaler()
        
    def _load_data(self, filename):
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"{path} not found. Run data_generator.py first.")
        return pd.read_csv(path)

    # ---------------------------------------------------------
    # Model 1 & 2: Isolation Forest Anomaly Detectors
    # ---------------------------------------------------------
    def train_mouse_model(self):
        """
        Model 2: Detect unnatural mouse trajectories using Isolation Forest.
        """
        print("\n=== Training Model 2 (Mouse Pattern Anomaly) ===")
        df = self._load_data("mouse_patterns.csv")
        
        # We assume label 0 is "Normal Human" and 1 is "Anomaly/Bot"
        X = df[['speed_variance', 'path_curvature', 'idle_duration']]
        y = df['is_bot'] # For evaluation only
        
        # Isolation Forest is unsupervised. Train ONLY on human data (Label 0)
        X_train_human = X[y == 0]
        
        # Scale
        X_scaled = self.scaler.fit_transform(X_train_human)
        joblib.dump(self.scaler, os.path.join(OUTPUT_DIR, "mouse_scaler.pkl"))
        
        # Train Unsupervised Anomaly Detector
        model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        model.fit(X_scaled)
        
        # Test on mixed data
        X_test_scaled = self.scaler.transform(X)
        y_pred = model.predict(X_test_scaled)
        # IF returns 1 for inlier, -1 for outlier. Map to our 0 (human), 1 (anomaly) labels
        y_pred_mapped = np.where(y_pred == -1, 1, 0)
        
        print("Mouse Model Validation Report:")
        print(classification_report(y, y_pred_mapped, target_names=["Human", "Bot"]))
        
        joblib.dump(model, os.path.join(OUTPUT_DIR, 'mouse_isolation_forest.pkl'))
        print(f"[OK] Saved mouse_isolation_forest.pkl")

    # ---------------------------------------------------------
    # Model 6: Core Ensemble Authenticity Classifier
    # ---------------------------------------------------------
    def train_core_ensemble(self):
        """
        Model 6: RandomForestClassifier evaluating all combined sensors.
        Uses SMOTE to handle class imbalance and StratifiedKFold for validation.
        """
        print("\n=== Training Model 6 (Fake Activity Core Ensemble) ===")
        df = self._load_data("behavior_ensemble.csv")
        
        X = df[['typing_entropy', 'mouse_entropy', 'gaze_presence', 'app_focus', 'emotion_focus']]
        y = df['behavior_class']
        
        # 1. Train/Test Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        
        # 2. Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        joblib.dump(self.scaler, os.path.join(OUTPUT_DIR, "ensemble_scaler.pkl"))
        
        # 3. SMOTE (Synthetic Minority Over-sampling) if classes are imbalanced
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X_train_scaled, y_train)
        
        # 4. Hyperparameter Tuning using GridSearchCV
        rf = RandomForestClassifier(random_state=42)
        param_grid = {
            'n_estimators': [50, 100],
            'max_depth': [None, 10, 20],
            'min_samples_split': [2, 5]
        }
        
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        print("Running GridSearchCV across 5-Folds...")
        grid = GridSearchCV(rf, param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
        grid.fit(X_res, y_res)
        
        best_model = grid.best_estimator_
        print(f"Best Parameters: {grid.best_params_}")
        
        # 5. Evaluate
        y_pred = best_model.predict(X_test_scaled)
        print("Core Ensemble Validation Report:")
        print(classification_report(y_test, y_pred, target_names=["Working", "Slacking", "Active Bot"]))
        
        # 6. Feature Importance Display (For SHAP)
        importances = best_model.feature_importances_
        for i, col in enumerate(X.columns):
            print(f"- {col}: {importances[i]*100:.1f}%")
        
        joblib.dump(best_model, os.path.join(OUTPUT_DIR, 'core_ensemble_rf.pkl'))
        print(f"[OK] Saved core_ensemble_rf.pkl")

if __name__ == "__main__":
    print("=== ProGuard ML Pipeline Orchestrator ===")
    
    # Generate fresh synthetic data right before training
    gen = SyntheticDataGenerator()
    gen.generate_mouse_trajectories(num_samples=1000)
    gen.generate_full_behavior_dataset(num_samples=2500)
    
    # Train and Save Models
    trainer = ProGuardModelTrainer()
    trainer.train_mouse_model()
    trainer.train_core_ensemble()
    
    print("\n[SUCCESS] Production ML Architecture Trained and Scalers Exported.")
