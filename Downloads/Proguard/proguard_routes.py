from datetime import datetime
from threading import Lock

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from proguard.analytics import ProGuardMonitor


proguard_bp = Blueprint('proguard', __name__)

_monitors = {}
_monitors_lock = Lock()


def _user_key() -> str:
    return str(getattr(current_user, 'id', 'anonymous'))


def _get_or_create_monitor() -> ProGuardMonitor:
    user_key = _user_key()
    with _monitors_lock:
        monitor = _monitors.get(user_key)
        if monitor is None:
            monitor = ProGuardMonitor(user_id=user_key)
            _monitors[user_key] = monitor
        return monitor





@proguard_bp.route('/api/proguard/start', methods=['POST'])
@login_required
def start_proguard_monitoring():
    try:
        monitor = _get_or_create_monitor()
        monitor.start_monitoring()
        return jsonify({
            'status': 'success',
            'message': 'ProGuard monitoring started',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@proguard_bp.route('/api/proguard/stop', methods=['POST'])
@login_required
def stop_proguard_monitoring():
    user_key = _user_key()
    try:
        with _monitors_lock:
            monitor = _monitors.get(user_key)
        if monitor is not None:
            monitor.stop_monitoring()
        return jsonify({'status': 'success', 'message': 'ProGuard monitoring stopped'})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@proguard_bp.route('/api/proguard/dashboard')
@login_required
def get_proguard_dashboard_data():
    user_key = _user_key()
    with _monitors_lock:
        monitor = _monitors.get(user_key)
    if monitor is None:
        return jsonify({'status': 'not_started', 'message': 'Monitoring not started'})

    try:
        data = monitor.get_current_dashboard_data()
        return jsonify({'status': 'success', 'data': data})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@proguard_bp.route('/api/proguard/break-recommendation')
@login_required
def get_break_recommendation():
    user_key = _user_key()
    with _monitors_lock:
        monitor = _monitors.get(user_key)
    if monitor is None:
        return jsonify({'recommended': False, 'status': 'not_started'})

    try:
        recommendation = monitor.trigger_break_recommendation()
        if isinstance(recommendation, dict):
            return jsonify(recommendation)
        return jsonify({'recommended': bool(recommendation)})
    except Exception as exc:
        return jsonify({'recommended': False, 'error': str(exc)}), 500


@proguard_bp.route('/api/proguard/generate-report', methods=['POST'])
@login_required
def generate_proguard_report():
    user_key = _user_key()
    with _monitors_lock:
        monitor = _monitors.get(user_key)
    if monitor is None:
        return jsonify({'status': 'error', 'message': 'Monitoring not started'}), 400

    try:
        report_path = monitor.generate_daily_report()
        return jsonify({'status': 'success', 'report_path': report_path})
    except Exception as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 500


@proguard_bp.route('/api/proguard/features')
@login_required
def get_proguard_features():
    features = [
        {'id': 1, 'name': 'Mouse & Keyboard Pattern Detection', 'status': 'Implemented'},
        {'id': 2, 'name': 'Screen Activity Monitor', 'status': 'Implemented'},
        {'id': 3, 'name': 'Typing Rhythm Analysis (LSTM)', 'status': 'Implemented'},
        {'id': 4, 'name': 'Webcam Gaze & Face Detection', 'status': 'Implemented'},
        {'id': 5, 'name': 'Emotion Detection via Face', 'status': 'Implemented'},
        {'id': 6, 'name': 'Work Authenticity Score', 'status': 'Implemented'},
        {'id': 7, 'name': 'Explainable AI (XAI)', 'status': 'Implemented'},
        {'id': 8, 'name': 'Real-Time Suspicion Heatmap', 'status': 'Implemented'},
        {'id': 9, 'name': 'Macro Pattern Detector', 'status': 'Implemented'},
        {'id': 10, 'name': 'AI-Based Break Recommender', 'status': 'Implemented'},
        {'id': 11, 'name': 'User Behavior Baseline Modeling', 'status': 'Implemented'},
        {'id': 12, 'name': 'Meeting App Monitor (Zoom/Meet)', 'status': 'Implemented'},
        {'id': 13, 'name': 'Emotion-to-Productivity Correlation', 'status': 'Integrated'},
        {'id': 14, 'name': 'Productive vs Time-Wasting App Ratio', 'status': 'Integrated'},
        {'id': 15, 'name': 'Smart Screenshot Analyzer', 'status': 'Implemented'},
        {'id': 16, 'name': 'Fake Activity Timeline Generator', 'status': 'Implemented'},
        {'id': 17, 'name': 'Self-Learning Mode (Semi-Supervised)', 'status': 'Implemented'},
        {'id': 18, 'name': 'Final Output Dashboard', 'status': 'Implemented'}
    ]
    return jsonify({'features': features})