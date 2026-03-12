import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

class SyntheticDataGenerator:
    """
    Generates high-fidelity adversarial synthetic data for training the ProGuard ML Models.
    Simulates human behavior (Gaussian variance, Fitts's Law) vs Bot behavior (Rigid loops).
    """
    
    def __init__(self, output_dir="src/proguard/data/synthetic"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_typing_sequences(self, num_samples=5000):
        """
        Model 1 (Typing Rhythm) Data:
        Humans have a natural Gaussian variance in keypress intervals (e.g., 100ms - 250ms).
        Macros have extremely rigid, low-variance intervals (e.g., exactly 50ms every time).
        """
        data = []
        labels = []
        
        for _ in range(num_samples):
            is_macro = np.random.rand() > 0.6  # 40% chance of being a macro
            
            if is_macro:
                # Rigorous macro: Same interval, very low variance
                base_interval = np.random.uniform(0.02, 0.1) # 20ms to 100ms
                intervals = np.random.normal(base_interval, 0.001, 15) # Very rigid
                labels.append(1) # 1 = Bot/Macro
            else:
                # Human typing: Higher base interval, higher variance depending on 'thought' gaps
                base_interval = np.random.uniform(0.1, 0.4)
                intervals = np.random.normal(base_interval, np.random.uniform(0.05, 0.15), 15)
                # Ensure no negative times
                intervals = np.abs(intervals)
                labels.append(0) # 0 = Human
                
            data.append(intervals.tolist())
            
        df = pd.DataFrame(data, columns=[f"interval_{i}" for i in range(15)])
        df['is_bot'] = labels
        
        output_path = os.path.join(self.output_dir, "typing_rhythm.csv")
        df.to_csv(output_path, index=False)
        print(f"[OK] Generated {num_samples} typing samples -> {output_path}")
        return df

    def generate_mouse_trajectories(self, num_samples=5000):
        """
        Model 2 (Mouse Pattern) Data:
        Features: Speed Variance, Path Curvature, Idle Duration.
        Humans decelerate before clicking (Fitts's Law). Bots move linearly or jump instantly.
        """
        data = []
        
        for _ in range(num_samples):
            is_bot = np.random.rand() > 0.7  # 30% chance of being an auto-clicker or jiggler
            
            if is_bot:
                # Jiggler: Tiny movements, constant speed, zero curvature OR Teleportation
                speed_variance = np.random.uniform(0.0, 0.05)
                path_curvature = np.random.uniform(0.0, 0.02) # Linear paths
                idle_duration = np.random.uniform(0.0, 0.1) # Never rests
                label = 1
            else:
                # Human: Rapid movements followed by slowing down and reading (idle)
                speed_variance = np.random.uniform(0.4, 0.9)
                path_curvature = np.random.uniform(0.2, 0.8) # Swooping arcs
                idle_duration = np.random.uniform(1.0, 15.0) # Rest periods
                label = 0
                
            data.append({
                'speed_variance': speed_variance,
                'path_curvature': path_curvature,
                'idle_duration': idle_duration,
                'is_bot': label
            })
            
        df = pd.DataFrame(data)
        output_path = os.path.join(self.output_dir, "mouse_patterns.csv")
        df.to_csv(output_path, index=False)
        print(f"[OK] Generated {num_samples} mouse trajectory samples -> {output_path}")
        return df

    def generate_full_behavior_dataset(self, num_samples=10000):
        """
        Model 6 (Fake Activity Core Ensemble) Data:
        Combines sensor inputs to predict overall work authenticity.
        """
        data = []
        
        for _ in range(num_samples):
            # 0: Good, 1: Slacking/Distracted, 2: Active Bot
            behavior_type = np.random.choice([0, 1, 2], p=[0.6, 0.25, 0.15])
            
            if behavior_type == 0: # Human Working
                t_ent = np.random.uniform(0.6, 1.0)
                m_ent = np.random.uniform(0.6, 1.0)
                gaze = np.random.uniform(0.7, 1.0)
                app = np.random.uniform(0.7, 1.0)
                emotion = np.random.uniform(0.5, 1.0)
                label = 0 # Authentic
                
            elif behavior_type == 1: # Human Slacking
                t_ent = np.random.uniform(0.1, 0.4)
                m_ent = np.random.uniform(0.2, 0.5)
                gaze = np.random.uniform(0.1, 0.5) # Looking at phone
                app = np.random.uniform(0.0, 0.3) # Netflix/YouTube
                emotion = np.random.uniform(0.1, 0.4) # Bored/Tired
                label = 1 # Suspicious/Slacking
                
            else: # Active Bot
                t_ent = np.random.uniform(0.0, 0.05) # Perfect loops
                m_ent = np.random.uniform(0.0, 0.05) 
                gaze = np.random.uniform(0.0, 0.2) # Nobody at desk
                app = np.random.uniform(0.8, 1.0) # But VS Code is "active"
                emotion = 0.0 # No face
                label = 2 # Bot/Fake
                
            data.append({
                'typing_entropy': t_ent,
                'mouse_entropy': m_ent,
                'gaze_presence': gaze,
                'app_focus': app,
                'emotion_focus': emotion,
                'behavior_class': label
            })
            
        df = pd.DataFrame(data)
        output_path = os.path.join(self.output_dir, "behavior_ensemble.csv")
        df.to_csv(output_path, index=False)
        print(f"[OK] Generated {num_samples} ensemble behavior samples -> {output_path}")
        return df

if __name__ == "__main__":
    print("=== ProGuard: Generating Advanced Synthetic Training Data ===")
    gen = SyntheticDataGenerator()
    gen.generate_typing_sequences()
    gen.generate_mouse_trajectories()
    gen.generate_full_behavior_dataset()
    print("=== Data Generation Complete ===")
