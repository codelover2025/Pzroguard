ProGuard - Deep Behavior Analytics for Work Authenticity
=======================================================

Overview
--------
ProGuard is an AI-powered system that distinguishes genuine work from fake activity in remote and online environments. It goes beyond time tracking by analyzing real human behavior while preserving privacy through data minimization and encryption.

Objective
---------
Build a behavior-driven productivity system that identifies authentic work by analyzing typing rhythm, mouse movement, screen usage, attention, and emotion signals.

Problem
-------
Conventional monitoring tools rely on activity duration, clicks, or screenshots. These signals can be spoofed by macros and jigglers, and they can expose sensitive information. They measure time, not authentic work.

Proposed Solution
-----------------
ProGuard uses multi-modal behavioral analysis:
- Typing rhythm analysis to detect automated patterns.
- Mouse movement analysis to detect robotic or repetitive activity.
- Gaze and face tracking to confirm presence and attention.
- Emotion detection to understand engagement.
- App usage tracking to separate productive vs non-productive time.

System Workflow
---------------
1. Data collection: mouse, keyboard, app usage, gaze, and emotion signals.
2. Data security and preprocessing: blur sensitive data, encrypt logs, clean inputs.
3. AI analysis: LSTM for typing rhythm, CNN for face and gaze, Isolation Forest for anomaly detection.
4. Explainability: SHAP or LIME explains why a score changed.
5. Visualization and reporting: dashboard, heatmaps, timelines, and exports.

Key Output
----------
- Work Authenticity Score (0-100).
- Clear explanations for flags (for example: repeated typing pattern and missing face for 20 minutes).
- Visual dashboards and reports for daily analysis.

Features (18)
-------------
1. Mouse and keyboard pattern detection
   - Detects fake or repetitive input activity such as macros or auto-jigglers.
2. Screen activity monitor
   - Tracks active application or window and time spent per app.
3. Typing rhythm analysis
   - Uses LSTM to detect unnatural typing consistency or speed.
4. Webcam gaze and face detection
   - Checks presence and attention using gaze direction and face detection.
5. Emotion detection via face
   - Classifies emotions (focused, neutral, bored, angry) from periodic frames.
6. Work Authenticity Score
   - Weighted fusion of all signals into a single score.
7. Explainable AI (XAI)
   - SHAP or LIME identifies the largest contributors to score changes.
8. Real-time suspicion heatmap
   - Color-coded time blocks showing productivity vs suspicious activity.
9. Macro pattern detector
   - Flags repeated sequences and timing anomalies in inputs.
10. AI-based break recommender
    - Suggests breaks when fatigue or inattention is detected.
11. User behavior baseline modeling
    - Learns each user's normal work patterns for personalized thresholds.
12. Meeting app monitor (Zoom/Meet)
    - Checks meeting engagement using app presence and camera or gaze signals.
13. Emotion-to-productivity correlation
    - Correlates emotion trends with productivity signals.
14. Productive vs time-wasting app ratio
    - Calculates productive time ratio from app usage logs.
15. Smart screenshot analyzer
    - Captures low-resolution screenshots and blurs sensitive content.
16. Fake activity timeline generator
    - Compiles suspicious periods into PDF or CSV reports.
17. Self-learning mode (semi-supervised)
    - Updates model weights using feedback and history.
18. Final output dashboard
    - Centralized dashboard with charts, scores, heatmaps, and exports.

Security and Privacy
--------------------
- AES encryption for logs and activity data.
- Automatic blurring of sensitive information before storage.
- No full video or audio storage; only derived metrics are saved.

Applications
------------
- Remote companies for employee productivity and authenticity.
- Educational institutions for online classes and assessments.
- Research labs and freelancers for accountability.
- Corporate environments for fair performance analytics.

Technologies
------------
- Python (pynput, psutil)
- OpenCV or dlib (vision)
- TensorFlow or PyTorch (ML)
- Flask (backend)
- React and D3.js (frontend)
- Matplotlib or ReportLab (reports)
- AES encryption (security)

Impact and Uniqueness
---------------------
ProGuard emphasizes fairness, authenticity, and privacy. It is not a surveillance tool, but a trust-building framework that detects fake activity while explaining the reasoning behind decisions.
