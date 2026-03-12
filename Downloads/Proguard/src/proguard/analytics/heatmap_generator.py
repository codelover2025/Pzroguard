"""
Feature 8: Real-Time Suspicion Heatmap
Visualizes productive and suspicious time blocks throughout the day
"""

import numpy as np
from datetime import datetime, timedelta, date
from typing import Optional
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64


class HeatmapGenerator:
    """
    Generates visual heatmaps of work authenticity over time
    Color-coded: Green = authentic, Yellow = suspicious, Red = very suspicious
    """
    
    def __init__(self, bucket_minutes=30):
        self.bucket_minutes = bucket_minutes  # Time buckets (e.g., 30 min)
        
        # Store authenticity scores by time
        self.time_scores = {}  # {timestamp: score}
    
    def add_score(self, timestamp, score):
        """
        Add authenticity score for a specific time
        
        Args:
            timestamp: datetime object
            score: authenticity score (0-100)
        """
        # Round to nearest bucket
        bucket = self._get_time_bucket(timestamp)
        
        self.time_scores[bucket] = score
    
    def _get_time_bucket(self, timestamp):
        """Round timestamp to nearest time bucket"""
        minutes = (timestamp.hour * 60 + timestamp.minute)
        bucket_minutes = (minutes // self.bucket_minutes) * self.bucket_minutes
        
        return timestamp.replace(
            hour=bucket_minutes // 60,
            minute=bucket_minutes % 60,
            second=0,
            microsecond=0
        )
    
    def generate_daily_heatmap(self, date=None):
        """
        Generate heatmap for a specific day
        
        Args:
            date: datetime.date object (default: today)
            
        Returns:
            Base64 encoded PNG image
        """
        if date is None:
            date = datetime.now().date()
        
        # Filter scores for this date
        day_scores = {
            ts: score for ts, score in self.time_scores.items()
            if ts.date() == date
        }
        
        if not day_scores:
            # Generate a blank placeholder heatmap instead of returning None
            fig, ax = plt.subplots(figsize=(10, 1))
            ax.text(0.5, 0.5, "Initializing Heatmap Data...", ha='center', va='center', color='gray')
            ax.set_axis_off()
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=80, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close(fig)
            return f'data:image/png;base64,{image_base64}'
        
        # Create time buckets for full day (00:00 to 23:59)
        buckets_per_day = (24 * 60) // self.bucket_minutes
        
        # Prepare data matrix (1 row x N columns for time)
        scores_array = []
        time_labels = []
        
        for i in range(buckets_per_day):
            bucket_time = datetime.combine(
                date,
                datetime.min.time()
            ) + timedelta(minutes=i * self.bucket_minutes)
            
            score = day_scores.get(bucket_time, -1)  # -1 = no data
            scores_array.append(score)
            
            # Create label every few hours
            if i % (120 // self.bucket_minutes) == 0:  # Every 2 hours
                time_labels.append(bucket_time.strftime('%H:%M'))
            else:
                time_labels.append('')
        
        # Reshape for heatmap (make it taller for better visibility)
        scores_matrix = np.array(scores_array).reshape(1, -1)
        scores_matrix = np.repeat(scores_matrix, 3, axis=0)  # Repeat rows
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(16, 3))
        
        # Custom colormap: Red (low) -> Yellow (mid) -> Green (high)
        cmap = sns.diverging_palette(10, 130, as_cmap=True)
        
        # Plot
        sns.heatmap(
            scores_matrix,
            cmap=cmap,
            vmin=0, vmax=100,
            cbar_kws={'label': 'Authenticity Score'},
            ax=ax,
            mask=(scores_matrix == -1),  # Hide no-data cells
            linewidths=0.5
        )
        
        # Set labels
        ax.set_xlabel('Time of Day')
        ax.set_ylabel('')
        ax.set_title(f'Work Authenticity Heatmap - {date}', fontsize=14, fontweight='bold')
        
        # Set x-axis labels
        ax.set_xticks(range(0, buckets_per_day, 120 // self.bucket_minutes))
        ax.set_xticklabels([
            time_labels[i] for i in range(0, buckets_per_day, 120 // self.bucket_minutes)
        ])
        
        ax.set_yticks([])
        
        plt.tight_layout()
        
        # Convert to base64 for web display
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return f'data:image/png;base64,{image_base64}'
    
    def generate_weekly_heatmap(self, start_date: Optional[date] = None):
        """
        Generate heatmap for a week (7 days x 24 hours)
        
        Args:
            start_date: datetime.date object (default: start of current week)
            
        Returns:
            Base64 encoded PNG image
        """
        if start_date is None:
            today_date = datetime.now().date()
            start_date = today_date - timedelta(days=today_date.weekday())  # Monday
        
        # Create 7-day matrix
        days = 7
        hours = 24
        
        scores_matrix = np.full((days, hours), -1.0)  # -1 = no data
        
        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            for hour in range(hours):
                # Get average score for this hour
                hour_scores = [
                    score for ts, score in self.time_scores.items()
                    if ts.date() == current_date and ts.hour == hour
                ]
                
                if hour_scores:
                    scores_matrix[day_offset, hour] = np.mean(hour_scores)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(14, 6))
        
        cmap = sns.diverging_palette(10, 130, as_cmap=True)
        
        sns.heatmap(
            scores_matrix,
            cmap=cmap,
            vmin=0, vmax=100,
            cbar_kws={'label': 'Authenticity Score'},
            ax=ax,
            mask=(scores_matrix == -1),
            linewidths=0.5
        )
        
        # Labels
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        ax.set_title(f'Weekly Work Authenticity Heatmap', fontsize=14, fontweight='bold')
        
        ax.set_xticklabels(range(24))
        ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return f'data:image/png;base64,{image_base64}'
    
    def get_suspicion_periods(self, threshold=40):
        """
        Get time periods with suspiciously low scores
        
        Args:
            threshold: Score below this is suspicious
            
        Returns:
            List of suspicious time periods
        """
        suspicious_periods = []
        
        sorted_times = sorted(self.time_scores.keys())
        
        period_start = None
        
        for ts in sorted_times:
            score = self.time_scores[ts]
            
            if score < threshold:
                if period_start is None:
                    period_start = ts
            else:
                if period_start is not None:
                    # End of suspicious period
                    suspicious_periods.append({
                        'start': period_start.isoformat(),
                        'end': ts.isoformat(),
                        'duration_minutes': (ts - period_start).total_seconds() / 60
                    })
                    period_start = None
        
        return suspicious_periods
    
    def get_summary_stats(self):
        """Get summary statistics of authenticity scores"""
        if not self.time_scores:
            return {}
        
        scores = list(self.time_scores.values())
        
        return {
            'average_score': float(np.mean(scores)),
            'median_score': float(np.median(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores)),
            'std_dev': float(np.std(scores)),
            'total_time_buckets': len(scores),
            'suspicious_periods': len(self.get_suspicion_periods())
        }
