"""
Feature 12: Meeting App Monitor (Zoom/Teams/Meet)
Detects if user is active in meetings or ghost-joining
"""

import time
from datetime import datetime
from collections import deque
import psutil

try:
    import win32gui
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class MeetingMonitor:
    """
    Monitors participation in video conferencing apps
    Detects ghost-joining (in meeting but not engaged)
    """
    
    MEETING_APPS = {
        'zoom': ['zoom.exe', 'zoom'],
        'teams': ['teams.exe', 'microsoft teams'],
        'meet': ['chrome.exe', 'firefox.exe'],  # Google Meet (browser-based)
        'webex': ['webex.exe', 'cisco webex'],
        'skype': ['skype.exe', 'skype']
    }
    
    MEETING_KEYWORDS = [
        'zoom meeting', 'teams meeting', 'meet.google.com',
        'webex', 'skype call'
    ]
    
    def __init__(self):
        self.current_meeting = None
        self.meeting_start_time = None
        self.meeting_history = deque(maxlen=100)
        
        # Engagement tracking
        self.camera_active = False
        self.mic_active = False
        self.webcam_monitor = None  # Reference to webcam monitor
    
    def detect_active_meeting(self):
        """
        Detect if user is currently in a meeting
        Returns: (in_meeting, app_name, meeting_title)
        """
        if not WINDOWS_AVAILABLE:
            return False, None, None
        
        # Get all running processes
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Check against meeting apps
                for app_type, app_names in self.MEETING_APPS.items():
                    for app_name in app_names:
                        if app_name in proc_name:
                            # Found meeting app running
                            
                            # Try to get window title
                            try:
                                hwnd = win32gui.GetForegroundWindow()
                                window_title = win32gui.GetWindowText(hwnd)
                                
                                # Check if window title indicates meeting
                                is_meeting = any(
                                    keyword in window_title.lower()
                                    for keyword in self.MEETING_KEYWORDS
                                )
                                
                                if is_meeting:
                                    return True, app_type, window_title
                                    
                            except:
                                # If can't get window, assume in meeting if app is running
                                return True, app_type, None
                                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False, None, None
    
    def check_camera_mic_status(self):
        """
        Check if camera/microphone is active
        Note: This is a simplified check - actual implementation
        would require OS-level permissions
        
        Returns: (camera_active, mic_active)
        """
        # Placeholder - actual implementation would check device access
        # For now, we'll estimate based on process names
        
        camera_active = False
        mic_active = False
        
        try:
            for proc in psutil.process_iter(['name']):
                proc_name = proc.info['name'].lower()
                
                # Heuristic: if video/audio related processes are running
                if 'camera' in proc_name or 'video' in proc_name:
                    camera_active = True
                if 'audio' in proc_name or 'microphone' in proc_name:
                    mic_active = True
                    
        except Exception:
            pass
        
        return camera_active, mic_active
    
    def link_webcam_monitor(self, webcam_monitor):
        """
        Link to WebcamMonitor for actual camera status
        
        Args:
            webcam_monitor: Instance of WebcamMonitor
        """
        self.webcam_monitor = webcam_monitor
    
    def calculate_engagement_score(self):
        """
        Calculate meeting engagement score
        Considers: camera on, mic on, face visible, gaze on screen
        
        Returns: engagement score (0-1)
        """
        if not self.current_meeting:
            return 0.0  # Not in meeting
        
        engagement_factors = []
        
        # Check camera/mic (estimated)
        camera_active, mic_active = self.check_camera_mic_status()
        engagement_factors.append(1.0 if camera_active else 0.0)
        engagement_factors.append(1.0 if mic_active else 0.5)  # Muted is ok sometimes
        
        # Check actual face presence (if webcam monitor linked)
        if self.webcam_monitor:
            presence_ratio = self.webcam_monitor.get_presence_ratio()
            attention_ratio = self.webcam_monitor.get_attention_ratio()
            
            engagement_factors.append(presence_ratio)
            engagement_factors.append(attention_ratio)
        
        # Calculate average
        if engagement_factors:
            return sum(engagement_factors) / len(engagement_factors)
        
        return 0.5  # Default moderate engagement
    
    def update_meeting_status(self):
        """Update current meeting status"""
        in_meeting, app_name, meeting_title = self.detect_active_meeting()
        
        current_time = time.time()
        
        # Meeting just started
        if in_meeting and not self.current_meeting:
            self.current_meeting = {
                'app': app_name,
                'title': meeting_title,
                'start_time': current_time,
                'engagement_checks': []
            }
            self.meeting_start_time = current_time
            print(f"🎥 Meeting started: {app_name}")
        
        # Meeting ongoing - check engagement
        elif in_meeting and self.current_meeting:
            engagement_score = self.calculate_engagement_score()
            
            self.current_meeting['engagement_checks'].append({
                'timestamp': current_time,
                'score': engagement_score
            })
        
        # Meeting ended
        elif not in_meeting and self.current_meeting:
            duration = current_time - self.meeting_start_time
            
            # Calculate average engagement
            engagement_scores = [
                check['score'] 
                for check in self.current_meeting['engagement_checks']
            ]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.5
            
            # Save to history
            meeting_record = {
                'app': self.current_meeting['app'],
                'title': self.current_meeting['title'],
                'duration_minutes': duration / 60,
                'average_engagement': avg_engagement,
                'start_time': datetime.fromtimestamp(self.meeting_start_time).isoformat(),
                'end_time': datetime.now().isoformat()
            }
            
            self.meeting_history.append(meeting_record)
            
            print(f"🎥 Meeting ended: {duration/60:.1f} min, engagement: {avg_engagement:.2f}")
            
            # Clear current meeting
            self.current_meeting = None
            self.meeting_start_time = None
    
    def get_current_metrics(self):
        """Get current meeting monitoring metrics"""
        if self.current_meeting:
            duration = time.time() - self.meeting_start_time
            engagement = self.calculate_engagement_score()
        else:
            duration = 0
            engagement = 0.0
        
        # Calculate daily meeting stats
        today_meetings = [
            m for m in self.meeting_history
            if m['start_time'].startswith(datetime.now().strftime('%Y-%m-%d'))
        ]
        
        total_meeting_time = sum(m['duration_minutes'] for m in today_meetings)
        avg_daily_engagement = (
            sum(m['average_engagement'] for m in today_meetings) / len(today_meetings)
            if today_meetings else 0.0
        )
        
        return {
            'in_meeting': self.current_meeting is not None,
            'current_meeting_duration_minutes': duration / 60 if duration else 0,
            'current_engagement': engagement,
            'meetings_today': len(today_meetings),
            'total_meeting_time_minutes': total_meeting_time,
            'average_daily_engagement': avg_daily_engagement,
            'meeting_history': list(self.meeting_history)[-5:],  # Last 5 meetings
            'timestamp': datetime.now().isoformat()
        }
