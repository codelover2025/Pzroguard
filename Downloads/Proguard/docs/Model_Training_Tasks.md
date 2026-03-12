# Model Training Tasks for Each Feature

## 1. Typing Rhythm / Keystroke Pattern Detection
**Goal:** Detect whether typing is natural or automated (macro).

**Data Needed:**
- Keystroke timestamps
- Key press intervals
- Typing speed variations
- Human typing vs macro typing samples

**Training Steps:**
1. Collect typing datasets (human vs automated).
2. Convert timestamps into sequences (time between key presses).
3. Normalize the sequence values.
4. Train sequence model (LSTM or RNN).
5. Evaluate classification accuracy.

**Output:** Probability of natural vs robotic typing.

---

## 2. Mouse Movement Pattern Detection
**Goal:** Detect unnatural mouse movements like jigglers.

**Data Needed:**
- Mouse coordinates (x,y)
- Movement speed
- Acceleration patterns
- Idle durations

**Training Steps:**
1. Record mouse trajectories.
2. Extract features (speed variance, path curvature).
3. Train anomaly detection model (Isolation Forest / Autoencoder).
4. Identify outliers.

**Output:** Suspicion score for robotic mouse movement.

---

## 3. Emotion Detection Model
**Goal:** Detect facial emotion from webcam frames.

**Data Needed:**
- Face images labeled with emotions.
- Dataset example: FER2013.

**Training Steps:**
1. Detect faces from images.
2. Resize images (e.g., 48x48 grayscale).
3. Train CNN model for classification.
4. Validate with accuracy metrics.

**Output:** Emotion label (Happy, Neutral, Angry, etc.).

*Note: You can also use a pretrained model like DeepFace instead of training from scratch.*

---

## 4. Gaze Tracking Model
**Goal:** Detect where the user is looking.

**Data Needed:**
- Eye region images
- Head pose angles
- Gaze direction labels

**Training Steps:**
1. Extract eye landmarks from face.
2. Calculate eye ratios or pupil position.
3. Train regression model or use geometric rules.
4. Predict gaze direction (Left, Right, Center).

**Output:** Attention status.

*Note: Most projects use geometric methods instead of training.*

---

## 5. User Behavior Baseline Model
**Goal:** Learn each user's normal work pattern.

**Data Needed:**
- Historical logs of:
  - typing speed
  - mouse activity
  - gaze presence
  - emotion distribution

**Training Steps:**
1. Collect behavior data for several sessions.
2. Build feature vectors.
3. Train baseline model (LSTM or clustering).
4. Compare new behavior to baseline.

**Output:** Deviation score.

---

## 6. Fake Activity Detection Model
**Goal:** Detect suspicious work patterns.

**Data Needed:**
- Combined feature set from all sensors.
- Features include:
  - typing rhythm
  - mouse randomness
  - gaze attention
  - emotion engagement
  - app usage time

**Training Steps:**
1. Combine features into dataset.
2. Train anomaly detection model.
3. Label suspicious sessions.

**Output:** Fake activity probability.

---

## 7. Emotion-to-Productivity Correlation Model
**Goal:** Understand how emotions affect productivity.

**Data Needed:**
- Emotion logs
- Typing speed
- mouse activity
- task completion time

**Training Steps:**
1. Compute productivity metrics.
2. Perform correlation analysis.
3. Train regression model.

**Output:** Productivity prediction.

---

## Models Summary

| Feature | Model Type |
|---------|------------|
| Typing Pattern | LSTM / RNN |
| Mouse Movement | Isolation Forest |
| Emotion Detection | CNN |
| Gaze Tracking | Landmark + regression |
| Behavior Baseline | LSTM / clustering |
| Fake Activity Detection | Anomaly detection |
| Emotion Productivity | Regression |
