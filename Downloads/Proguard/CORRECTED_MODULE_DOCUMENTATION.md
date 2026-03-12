# ProGuard Module Documentation (Corrected)

This document provides accurate descriptions and sample code for the core modules of the ProGuard Work Authenticity system, reflecting the current codebase implementation.

## 3.1 Pattern Detection Module
The pattern detection module analyzes typing rhythm and mouse movement to identify repetitive or automated activity. It uses advanced statistical methods and machine learning to distinguish between human and bot-like behavior.

### Algorithms and Methods
1. **Keystroke Timing**: Captures inter-keystroke intervals (IKI).
2. **LSTM Neural Network**: A Deep Learning model (Long Short-Term Memory) classifies typing sequences as "human" or "bot" based on temporal patterns.
3. **Shannon Entropy**: Calculates the randomness of typing and mouse movements. Low entropy indicates highly repetitive, suspicious patterns (macros/jitglers).
4. **Macro Sequence Detection**: Identifies repeated identical input sequences.

### Sample Code (Typing Rhythm Analysis)
```python
from src.proguard.analytics.typing_rhythm import TypingRhythmAnalyzer

analyzer = TypingRhythmAnalyzer()

# Collect keystrokes
analyzer.add_keystroke(timestamp=time.time(), key_char='a')

# Get authenticity metrics
metrics = analyzer.get_current_metrics()
# metrics['typing_authenticity'] -> 0 to 1 (bot to human)
# metrics['rhythm_entropy'] -> normalized randomness
```

---

## 3.2 Emotion Detection Module
The emotion detection module analyzes facial expressions in real-time to correlate emotional state with workplace engagement.

### Implementation Details
- **Primary Engine**: `DeepFace` library for convolutional neural network (CNN) based emotion classification.
- **Fallback**: Simple brightness/contrast heuristics if DeepFace is unavailable.
- **Detections**: Happy, Neutral, Angry, Sad, Surprised, Fear, Disgust.

### Sample Code (Emotion Analysis)
```python
from deepface import DeepFace
import cv2

def detect_emotion(frame):
    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
    # result[0]['dominant_emotion'] returns the primary emotion
    return result[0]['dominant_emotion']
```

---

## 3.3 Gaze Tracking Module
The gaze tracking module monitors the user's attention by detecting if they are looking at the active workspace.

### Real-World Logic
Unlike generic gaze libraries, ProGuard utilizes **Haar Cascades** for low-latency eye visibility detection:
1. Detect face region using `haarcascade_frontalface_default.xml`.
2. Locate eye regions using `haarcascade_eye.xml`.
3. **Gaze Condition**: If both eyes are visible and centered within the face region, the user is marked as "Looking at Screen".

### Sample Code (Gaze Detection)
```python
import cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def check_gaze(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        face_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(face_gray)
        if len(eyes) >= 2:
            return "Looking at screen"
    return "Looking away"
```

---

## 3.4 Work Authenticity Score Calculation
The system aggregates signals into a single "Authenticity Score" (0-100) using a multi-factor penalty and reward system.

### Scoring Parameters
- **Typing Entropy**: Low variability reduces score.
- **Mouse Entropy**: Robotic, repetitive movements reduce score.
- **Gaze Presence**: Time spent looking away reduces score.
- **App Focus**: Usage of non-productive applications reduces score.
- **Emotion Focus**: Positive/Neutral expressions provide rewards; negative expressions or lack of face presence reduce score.

### Scoring Logic
```python
def calculate_score(signals):
    score = 100.0
    penalties = 0.0
    
    if signals['gaze_presence'] < 0.5:
        penalties += (0.5 - signals['gaze_presence']) * 40.0
    
    if signals['typing_entropy'] < 0.35:
        penalties += (0.35 - signals['typing_entropy']) * 40.0
        
    # Final Score clamp
    return max(0, min(100, 100 - penalties))
```

---

## 3.5 Report Generation Module
ProGuard generates detailed PDF reports that provide a timeline of work authenticity and behavior analytics.

### Features
- **Visual Timelines**: Graphs showing score fluctuations throughout the day.
- **Event Logging**: Timestamps for suspicious activity (macros, looking away).
- **Statistical Summaries**: Average authenticity, dominant emotions, and focus ratios.

### Sample Code (Generating Daily PDF)
```python
from src.proguard.analytics.proguard_monitor import ProGuardMonitor

monitor = ProGuardMonitor(user_id="V001")
# After monitoring session
report_path = monitor.generate_daily_report(output_path='reports')
print(f"Report saved to: {report_path}")
```
