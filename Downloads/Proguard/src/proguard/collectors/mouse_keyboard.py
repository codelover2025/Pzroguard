"""
Feature 1: Mouse & Keyboard Pattern Detection
Detects fake or repetitive input activity such as macros or auto-jigglers
"""

import time
import json
import threading
from datetime import datetime
from collections import deque
from pynput import mouse, keyboard
import numpy as np
from ..storage import SecureStorage


class MouseKeyboardCollector:
    """
    Monitors mouse and keyboard activity to detect patterns
    Calculates entropy to identify bot-like behavior
    """
    
    def __init__(self, window_size=100, storage_path='data/input_logs',
                 on_key_press_callback=None, on_mouse_move_callback=None):
        self.window_size = window_size
        self.storage = SecureStorage(storage_path)

        # External callbacks (used by ProGuardMonitor to feed analyzers)
        self.on_key_press_callback = on_key_press_callback
        self.on_mouse_move_callback = on_mouse_move_callback

        # Mouse data
        self.mouse_positions = deque(maxlen=window_size)
        self.mouse_times = deque(maxlen=window_size)
        self.mouse_clicks = deque(maxlen=window_size)
        
        # Keyboard data
        self.key_presses = deque(maxlen=window_size)
        self.key_times = deque(maxlen=window_size)
        
        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None
        self.running = False
        
    def on_mouse_move(self, x, y):
        """Callback for mouse movement"""
        timestamp = time.time()
        self.mouse_positions.append((x, y))
        self.mouse_times.append(timestamp)
        # Forward to external analyzer callback if registered
        if self.on_mouse_move_callback:
            try:
                self.on_mouse_move_callback(x, y, timestamp)
            except Exception:
                pass
        
    def on_mouse_click(self, x, y, button, pressed):
        """Callback for mouse clicks"""
        if pressed:
            timestamp = time.time()
            self.mouse_clicks.append({
                'x': x, 'y': y,
                'button': str(button),
                'time': timestamp
            })
    
    def on_key_press(self, key):
        """Callback for key presses"""
        timestamp = time.time()
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        self.key_presses.append(key_char)
        self.key_times.append(timestamp)
        # Forward to external analyzer callback if registered
        if self.on_key_press_callback:
            try:
                self.on_key_press_callback(key_char, timestamp)
            except Exception:
                pass
    
    def calculate_mouse_entropy(self):
        """
        Calculate entropy of mouse movements
        Low entropy = repetitive patterns (suspicious)
        """
        if len(self.mouse_positions) < 10:
            return 0.0  # Not enough data
        
        # Calculate movement vectors
        positions = list(self.mouse_positions)
        dx = np.diff([p[0] for p in positions])
        dy = np.diff([p[1] for p in positions])
        
        # Calculate angles
        angles = np.arctan2(dy, dx)
        
        # Bin angles and calculate entropy
        hist, _ = np.histogram(angles, bins=16, range=(-np.pi, np.pi))
        hist = hist / hist.sum()  # Normalize
        
        # Shannon entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        normalized_entropy = entropy / np.log2(16)  # Normalize to 0-1
        
        return normalized_entropy
    
    def calculate_keyboard_entropy(self):
        """
        Calculate entropy of keystroke timing
        Constant intervals = macro/bot (suspicious)
        """
        if len(self.key_times) < 10:
            return 0.0  # Not enough data
        
        # Calculate inter-keystroke intervals
        times = list(self.key_times)
        intervals = np.diff(times)
        
        # Bin intervals and calculate entropy
        hist, _ = np.histogram(intervals, bins=20)
        hist = hist / hist.sum()  # Normalize
        
        # Shannon entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        normalized_entropy = entropy / np.log2(20)  # Normalize to 0-1
        
        return normalized_entropy
    
    def detect_macro_pattern(self):
        """
        Detect repeated identical sequences (macro indicator)
        Returns: True if macro pattern detected
        """
        if len(self.key_presses) < 20:
            return False
        
        # Check for repeated sequences
        keys = list(self.key_presses)
        times = list(self.key_times)
        
        # Look for identical timing patterns
        intervals = np.diff(times)
        
        # Check if standard deviation is very low (constant timing)
        if len(intervals) > 10:
            std_dev = np.std(intervals)
            mean_interval = np.mean(intervals)
            
            # Coefficient of variation < 0.1 suggests macro
            if mean_interval > 0 and (std_dev / mean_interval) < 0.1:
                return True
        
        return False
    
    def get_current_metrics(self):
        """
        Get current input pattern metrics
        Returns normalized scores (0-1)
        """
        return {
            'mouse_entropy': self.calculate_mouse_entropy(),
            'keyboard_entropy': self.calculate_keyboard_entropy(),
            'macro_detected': self.detect_macro_pattern(),
            'total_mouse_moves': len(self.mouse_positions),
            'total_key_presses': len(self.key_presses),
            'total_clicks': len(self.mouse_clicks),
            'timestamp': datetime.now().isoformat()
        }
    
    def save_logs(self):
        """Save encrypted activity logs"""
        data = {
            'mouse_positions': list(self.mouse_positions),
            'mouse_times': list(self.mouse_times),
            'key_times': list(self.key_times),
            'metrics': self.get_current_metrics()
        }
        
        self.storage.save_encrypted(f'input_log_{datetime.now().strftime("%Y%m%d")}.json', data)
    
    def start(self):
        """Start monitoring"""
        self.running = True
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self.on_mouse_move,
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_key_press
        )
        self.keyboard_listener.start()
        
        print("[OK] Mouse & Keyboard monitoring started")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        
        # Save final logs
        self.save_logs()
        
        print("[STOPPED] Mouse & Keyboard monitoring stopped")
