"""
Feature 15: Smart Screenshot Analyzer
Takes automatic screenshots but blurs private info using OCR + AI
"""

import time
import threading
from datetime import datetime
from pathlib import Path
import numpy as np

try:
    import pyautogui
    import cv2
    from PIL import Image, ImageFilter
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False

try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

from ..storage import SecureStorage


class ScreenshotAnalyzer:
    """
    Captures periodic screenshots with privacy protection
    Analyzes screen content to classify activity
    """
    
    # Activity classification keywords
    ACTIVITY_KEYWORDS = {
        'coding': ['python', 'javascript', 'java', 'function', 'class', 'import', 'def', 'var', 'const'],
        'documentation': ['readme', 'documentation', 'docs', 'wiki', 'confluence'],
        'communication': ['email', 'slack', 'teams', 'chat', 'message'],
        'browsing': ['chrome', 'firefox', 'safari', 'browser', 'google'],
        'entertainment': ['youtube', 'netflix', 'spotify', 'video', 'music'],
        'social_media': ['facebook', 'twitter', 'instagram', 'reddit', 'linkedin']
    }
    
    # Sensitive data patterns (to blur)
    SENSITIVE_PATTERNS = [
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b\d{16}\b',  # Credit card
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'  # Phone
    ]
    
    def __init__(self, interval=300, storage_path='data/screenshots', blur_sensitive=True):
        self.interval = interval  # seconds between screenshots (default 5 min)
        self.storage = SecureStorage(storage_path)
        self.blur_sensitive = blur_sensitive
        
        # Screenshot storage
        self.screenshot_dir = Path(storage_path) / 'images'
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Analysis results
        self.screenshot_analyses = []
        
        # Running state
        self.running = False
        self.capture_thread = None
    
    def capture_screenshot(self):
        """
        Capture screenshot of current screen
        Returns: PIL Image object
        """
        if not SCREENSHOT_AVAILABLE:
            return None
        
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"[WARNING] Screenshot capture failed: {e}")
            return None
    
    def detect_sensitive_regions(self, image):
        """
        Detect regions containing sensitive information using OCR
        
        Returns: List of (x, y, w, h) bounding boxes to blur
        """
        if not OCR_AVAILABLE:
            return []
        
        try:
            # Convert PIL to OpenCV format
            img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Perform OCR with bounding boxes
            ocr_data = pytesseract.image_to_data(img_cv, output_type=pytesseract.Output.DICT)
            
            sensitive_regions = []
            
            # Check each detected text region
            for i, text in enumerate(ocr_data['text']):
                # Check against sensitive patterns
                import re
                for pattern in self.SENSITIVE_PATTERNS:
                    if re.search(pattern, text):
                        # Get bounding box
                        x = ocr_data['left'][i]
                        y = ocr_data['top'][i]
                        w = ocr_data['width'][i]
                        h = ocr_data['height'][i]
                        
                        sensitive_regions.append((x, y, w, h))
                        break
            
            return sensitive_regions
            
        except Exception as e:
            print(f"[WARNING] Sensitive region detection failed: {e}")
            return []
    
    def blur_regions(self, image, regions):
        """
        Blur specified regions in image
        
        Args:
            image: PIL Image
            regions: List of (x, y, w, h) tuples
            
        Returns: Blurred PIL Image
        """
        img_array = np.array(image)
        
        for (x, y, w, h) in regions:
            # Extract region
            region = img_array[y:y+h, x:x+w]
            
            # Apply Gaussian blur
            blurred_region = cv2.GaussianBlur(region, (51, 51), 0)
            
            # Replace region
            img_array[y:y+h, x:x+w] = blurred_region
        
        return Image.fromarray(img_array)
    
    def classify_activity(self, screenshot):
        """
        Classify what activity is shown in screenshot
        Uses OCR to extract text and keyword matching
        
        Returns: activity category string
        """
        if not OCR_AVAILABLE:
            return 'unknown'
        
        try:
            # Convert to grayscale for better OCR
            gray = screenshot.convert('L')
            
            # Extract text
            text = pytesseract.image_to_string(gray).lower()
            
            # Match against keyword categories
            category_scores = {}
            
            for category, keywords in self.ACTIVITY_KEYWORDS.items():
                score = sum(1 for keyword in keywords if keyword in text)
                category_scores[category] = score
            
            # Get category with highest score
            if category_scores:
                best_category = max(category_scores.items(), key=lambda x: x[1])
                if best_category[1] > 0:
                    return best_category[0]
            
            return 'unknown'
            
        except Exception as e:
            print(f"[WARNING] Activity classification failed: {e}")
            return 'unknown'
    
    def process_screenshot(self):
        """
        Capture and process screenshot with privacy protection
        Returns: analysis dict
        """
        # Capture screenshot
        screenshot = self.capture_screenshot()
        if not screenshot:
            return None
        
        # Classify activity
        activity = self.classify_activity(screenshot)
        
        # Detect and blur sensitive regions
        if self.blur_sensitive:
            sensitive_regions = self.detect_sensitive_regions(screenshot)
            if sensitive_regions:
                screenshot = self.blur_regions(screenshot, sensitive_regions)
                blurred_count = len(sensitive_regions)
            else:
                blurred_count = 0
        else:
            blurred_count = 0
        
        # Save screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screen_{timestamp}.png'
        filepath = self.screenshot_dir / filename
        
        # Compress to save space
        screenshot.save(filepath, 'PNG', optimize=True, quality=85)
        
        # Create analysis record
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'filename': filename,
            'activity': activity,
            'sensitive_regions_blurred': blurred_count,
            'file_size_kb': filepath.stat().st_size / 1024
        }
        
        self.screenshot_analyses.append(analysis)
        
        return analysis
    
    def capture_loop(self):
        """Main screenshot capture loop"""
        while self.running:
            try:
                self.process_screenshot()
            except Exception as e:
                print(f"[ERROR] Screenshot processing error: {e}")
            
            time.sleep(self.interval)
    
    def get_current_metrics(self):
        """Get screenshot analysis metrics"""
        if not self.screenshot_analyses:
            return {
                'total_screenshots': 0,
                'activity_distribution': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate activity distribution
        activity_counts = {}
        for analysis in self.screenshot_analyses:
            activity = analysis['activity']
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        # Convert to percentages
        total = len(self.screenshot_analyses)
        activity_distribution = {
            activity: (count / total) * 100
            for activity, count in activity_counts.items()
        }
        
        return {
            'total_screenshots': total,
            'activity_distribution': activity_distribution,
            'recent_analyses': self.screenshot_analyses[-10:],  # Last 10
            'total_storage_mb': sum(
                a['file_size_kb'] for a in self.screenshot_analyses
            ) / 1024,
            'timestamp': datetime.now().isoformat()
        }
    
    def start(self):
        """Start screenshot capture"""
        if not SCREENSHOT_AVAILABLE:
            print("[WARNING] Screenshot capture not available (pyautogui/cv2 missing)")
            return
        
        self.running = True
        self.capture_thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.capture_thread.start()
        
        print(f"[OK] Screenshot analyzer started (interval: {self.interval}s)")
    
    def stop(self):
        """Stop screenshot capture"""
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        # Save analysis log
        self.storage.save_encrypted(
            f'screenshot_analysis_{datetime.now().strftime("%Y%m%d")}.json',
            {'analyses': self.screenshot_analyses}
        )
        
        print("[STOPPED] Screenshot analyzer stopped")
