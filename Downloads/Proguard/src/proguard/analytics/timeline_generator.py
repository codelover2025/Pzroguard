"""
Feature 16: Fake Activity Timeline Generator
Generates detailed report of fake vs real activity periods
"""

from datetime import datetime, timedelta
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch


class TimelineGenerator:
    """
    Generates comprehensive timeline reports
    Highlights fake vs authentic activity periods
    """
    
    def __init__(self):
        self.events = []  # List of timeline events
    
    def add_event(self, timestamp, event_type, description, authenticity_score, details=None):
        """
        Add event to timeline
        
        Args:
            timestamp: datetime
            event_type: Event category (e.g., 'keyboard', 'mouse', 'meeting')
            description: Human-readable description
            authenticity_score: Score 0-100
            details: Additional details dict
        """
        self.events.append({
            'timestamp': timestamp,
            'type': event_type,
            'description': description,
            'authenticity_score': authenticity_score,
            'details': details or {},
            'is_fake': authenticity_score < 40  # Below 40 = likely fake
        })
    
    def generate_timeline_data(self, start_date=None, end_date=None):
        """
        Generate timeline data structure for a date range
        
        Returns:
            Dict with timeline segments (fake vs real)
        """
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
        if end_date is None:
            end_date = datetime.now()
        
        # Filter events
        filtered_events = [
            e for e in self.events
            if start_date <= e['timestamp'] <= end_date
        ]
        
        # Sort by timestamp
        filtered_events.sort(key=lambda x: x['timestamp'])
        
        # Create segments
        segments = []
        
        for i, event in enumerate(filtered_events):
            segment = {
                'start_time': event['timestamp'].isoformat(),
                'type': event['type'],
                'description': event['description'],
                'score': event['authenticity_score'],
                'status': 'fake' if event['is_fake'] else 'real',
                'details': event['details']
            }
            
            # Calculate duration (to next event or end)
            if i < len(filtered_events) - 1:
                next_event = filtered_events[i + 1]
                duration = (next_event['timestamp'] - event['timestamp']).total_seconds() / 60
            else:
                duration = 1  # Default 1 minute for last event
            
            segment['duration_minutes'] = duration
            
            segments.append(segment)
        
        # Calculate statistics
        total_time = sum(s['duration_minutes'] for s in segments)
        fake_time = sum(s['duration_minutes'] for s in segments if s['status'] == 'fake')
        real_time = total_time - fake_time
        
        return {
            'segments': segments,
            'summary': {
                'total_time_minutes': total_time,
                'fake_time_minutes': fake_time,
                'real_time_minutes': real_time,
                'fake_percentage': (fake_time / total_time * 100) if total_time > 0 else 0,
                'total_events': len(segments)
            }
        }
    
    def generate_pdf_report(self, filepath, start_date=None, end_date=None):
        """
        Generate PDF report with timeline
        
        Args:
            filepath: Path to save PDF
            start_date: Start of date range
            end_date: End of date range
        """
        timeline_data = self.generate_timeline_data(start_date, end_date)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(
            "<b>ProGuard Work Authenticity Timeline Report</b>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Date range
        date_text = f"Report Period: {start_date.strftime('%Y-%m-%d %H:%M') if start_date else 'N/A'} to {end_date.strftime('%Y-%m-%d %H:%M') if end_date else 'N/A'}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary section
        summary = timeline_data['summary']
        
        summary_text = f"""
        <b>Summary:</b><br/>
        Total Time Analyzed: {summary['total_time_minutes']:.1f} minutes<br/>
        Authentic Activity: {summary['real_time_minutes']:.1f} minutes ({100-summary['fake_percentage']:.1f}%)<br/>
        Fake/Suspicious Activity: {summary['fake_time_minutes']:.1f} minutes ({summary['fake_percentage']:.1f}%)<br/>
        Total Events: {summary['total_events']}
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Timeline table
        story.append(Paragraph("<b>Detailed Timeline:</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        # Table data
        table_data = [['Time', 'Type', 'Description', 'Score', 'Status', 'Duration (min)']]
        
        for segment in timeline_data['segments'][:50]:  # Limit to 50 events
            table_data.append([
                segment['start_time'].split('T')[1][:5],  # HH:MM
                segment['type'],
                segment['description'][:30] + '...' if len(segment['description']) > 30 else segment['description'],
                f"{segment['score']:.0f}",
                segment['status'].upper(),
                f"{segment['duration_minutes']:.1f}"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1*inch, 1*inch, 2.5*inch, 0.7*inch, 0.8*inch, 1*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        # Color-code status column
        for i, segment in enumerate(timeline_data['segments'][:50], start=1):
            if segment['status'] == 'fake':
                table.setStyle(TableStyle([
                    ('BACKGROUND', (4, i), (4, i), colors.red),
                    ('TEXTCOLOR', (4, i), (4, i), colors.white)
                ]))
        
        story.append(table)
        
        # Build PDF
        doc.build(story)
        
        print(f"[OK] Timeline report generated: {filepath}")
        
        return filepath
    
    def get_hourly_distribution(self):
        """
        Get distribution of fake vs real activity by hour of day
        
        Returns:
            Dict with hourly breakdown
        """
        hourly_data = {hour: {'fake': 0, 'real': 0} for hour in range(24)}
        
        for event in self.events:
            hour = event['timestamp'].hour
            status = 'fake' if event['is_fake'] else 'real'
            hourly_data[hour][status] += 1
        
        return hourly_data
    
    def get_pattern_analysis(self):
        """
        Analyze patterns in fake activity
        
        Returns:
            Pattern insights dict
        """
        if not self.events:
            return {'patterns': []}
        
        fake_events = [e for e in self.events if e['is_fake']]
        
        # Analyze by hour
        fake_by_hour = {}
        for event in fake_events:
            hour = event['timestamp'].hour
            fake_by_hour[hour] = fake_by_hour.get(hour, 0) + 1
        
        # Find peak fake hours
        if fake_by_hour:
            peak_hour = max(fake_by_hour.items(), key=lambda x: x[1])
        else:
            peak_hour = None
        
        # Analyze by type
        fake_by_type = {}
        for event in fake_events:
            event_type = event['type']
            fake_by_type[event_type] = fake_by_type.get(event_type, 0) + 1
        
        return {
            'total_fake_events': len(fake_events),
            'fake_percentage': len(fake_events) / len(self.events) * 100 if self.events else 0,
            'peak_fake_hour': peak_hour[0] if peak_hour else None,
            'most_common_fake_type': max(fake_by_type.items(), key=lambda x: x[1])[0] if fake_by_type else None,
            'fake_by_type': fake_by_type,
            'fake_by_hour': fake_by_hour
        }
