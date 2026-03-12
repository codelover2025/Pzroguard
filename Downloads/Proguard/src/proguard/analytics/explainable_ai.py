"""
Feature 7: Explainable AI (XAI)
Explains why a score dropped or user was flagged
"""

import numpy as np
from datetime import datetime


class ExplainableAI:
    """
    Provides human-readable explanations for ProGuard authenticity scores
    Uses feature importance and threshold analysis
    """
    
    # Feature thresholds for suspicion
    THRESHOLDS = {
        'typing_entropy': 0.3,  # Below this = suspicious
        'mouse_entropy': 0.3,
        'gaze_presence': 0.5,  # Below this = not present enough
        'app_focus': 0.4,  # Below this = too much non-productive time
        'emotion_focus': 0.3,  # Below this = disengaged
        'anomaly_score': 0.7,  # Above this = anomalous behavior
    }
    
    # Feature weights (importance)
    WEIGHTS = {
        'typing_entropy': 0.20,
        'mouse_entropy': 0.15,
        'gaze_presence': 0.25,
        'app_focus': 0.20,
        'emotion_focus': 0.10,
        'anomaly_score': 0.10,
    }
    
    def __init__(self):
        # Override weights dynamically using trained ML Model Importance
        try:
            import joblib
            import os
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'models', 'trained', 'core_ensemble_rf.pkl')
            core_model = joblib.load(model_path)
            
            # The features in the training script were:
            # ['typing_entropy', 'mouse_entropy', 'gaze_presence', 'app_focus', 'emotion_focus']
            importances = core_model.feature_importances_
            
            self.WEIGHTS = {
                'typing_entropy': float(importances[0]),
                'mouse_entropy': float(importances[1]),
                'gaze_presence': float(importances[2]),
                'app_focus': float(importances[3]),
                'emotion_focus': float(importances[4]),
                'anomaly_score': 0.15 # Keep a base weight for anomaly score cascading
            }
            print(f"[INFO] SHAP XAI: Loaded true ML Feature Importances: {self.WEIGHTS}")
        except Exception as e:
            print(f"[WARNING] SHAP XAI: ML Models not found, using heuristic weights.")
    
    def explain_score(self, signals, final_score):
        """
        Generate explanation for the authenticity score
        
        Args:
            signals: Dict of normalized signal values (0-1)
            final_score: Final authenticity score (0-100)
            
        Returns:
            Dict with explanation, contributing factors, and recommendations
        """
        reasons = []
        positive_factors = []
        negative_factors = []
        
        # Analyze each signal
        for feature, value in signals.items():
            threshold = self.THRESHOLDS.get(feature, 0.5)
            weight = self.WEIGHTS.get(feature, 0.1)
            
            # Calculate impact
            if feature == 'anomaly_score':
                # Higher anomaly = negative
                if value > threshold:
                    impact = (value - threshold) * weight * 100
                    reasons.append(self._get_reason_text(feature, value, 'high'))
                    negative_factors.append({
                        'feature': feature,
                        'value': value,
                        'impact': -impact,
                        'description': self._get_feature_description(feature)
                    })
                else:
                    impact = (threshold - value) * weight * 100
                    positive_factors.append({
                        'feature': feature,
                        'value': value,
                        'impact': impact,
                        'description': self._get_feature_description(feature)
                    })
            else:
                # Lower value = negative
                if value < threshold:
                    impact = (threshold - value) * weight * 100
                    reasons.append(self._get_reason_text(feature, value, 'low'))
                    negative_factors.append({
                        'feature': feature,
                        'value': value,
                        'impact': -impact,
                        'description': self._get_feature_description(feature)
                    })
                else:
                    impact = (value - threshold) * weight * 100
                    positive_factors.append({
                        'feature': feature,
                        'value': value,
                        'impact': impact,
                        'description': self._get_feature_description(feature)
                    })
        
        # Sort by impact
        negative_factors.sort(key=lambda x: x['impact'])
        positive_factors.sort(key=lambda x: x['impact'], reverse=True)
        
        # Generate overall assessment
        if final_score >= 80:
            assessment = "High authenticity - work behavior appears genuine"
        elif final_score >= 60:
            assessment = "Moderate authenticity - some concerns detected"
        elif final_score >= 40:
            assessment = "Low authenticity - multiple red flags detected"
        else:
            assessment = "Very low authenticity - strong evidence of inauthentic behavior"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(negative_factors)
        
        return {
            'final_score': final_score,
            'assessment': assessment,
            'primary_reasons': reasons[:3],  # Top 3 reasons
            'negative_factors': negative_factors,
            'positive_factors': positive_factors,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_reason_text(self, feature, value, severity):
        """Get human-readable reason text"""
        reasons_map = {
            'typing_entropy': {
                'low': f"Typing pattern appears repetitive or automated (entropy: {value:.2f})",
                'high': f"Typing pattern shows natural variation"
            },
            'mouse_entropy': {
                'low': f"Mouse movements show low variation (entropy: {value:.2f})",
                'high': f"Mouse movements appear natural"
            },
            'gaze_presence': {
                'low': f"Low screen attention detected ({value*100:.0f}% presence)",
                'high': f"Good screen attention maintained"
            },
            'app_focus': {
                'low': f"High non-productive app usage ({value*100:.0f}% productive)",
                'high': f"Strong focus on productive applications"
            },
            'emotion_focus': {
                'low': f"Emotional engagement appears low (score: {value:.2f})",
                'high': f"Good emotional engagement detected"
            },
            'anomaly_score': {
                'high': f"Anomalous behavior patterns detected (score: {value:.2f})",
                'low': f"Behavior consistent with baseline"
            }
        }
        
        return reasons_map.get(feature, {}).get(severity, f"{feature}: {value:.2f}")
    
    def _get_feature_description(self, feature):
        """Get feature description"""
        descriptions = {
            'typing_entropy': "Measures randomness in typing patterns",
            'mouse_entropy': "Measures randomness in mouse movements",
            'gaze_presence': "Percentage of time face detected on screen",
            'app_focus': "Ratio of productive to non-productive app usage",
            'emotion_focus': "Engagement level based on facial expressions",
            'anomaly_score': "Deviation from established baseline behavior"
        }
        
        return descriptions.get(feature, "Unknown feature")
    
    def _generate_recommendations(self, negative_factors):
        """Generate actionable recommendations"""
        recommendations = []
        
        for factor in negative_factors[:3]:  # Top 3 issues
            feature = factor['feature']
            
            rec_map = {
                'typing_entropy': "Check for keyboard macros or automated input tools",
                'mouse_entropy': "Verify mouse jiggler or automation software is not running",
                'gaze_presence': "Ensure user is present at workstation during work hours",
                'app_focus': "Review application usage for excessive non-work activities",
                'emotion_focus': "User may need break or engagement support",
                'anomaly_score': "Investigate unusual behavior patterns - potential policy violation"
            }
            
            rec = rec_map.get(feature, f"Review {feature} data")
            recommendations.append(rec)
        
        return recommendations
    
    def explain_trend(self, historical_scores, current_score):
        """
        Explain score trends over time
        
        Args:
            historical_scores: List of past scores
            current_score: Current score
            
        Returns:
            Trend analysis dict
        """
        if len(historical_scores) < 2:
            return {
                'trend': 'insufficient_data',
                'description': 'Not enough historical data for trend analysis'
            }
        
        # Calculate trend
        scores = np.array(historical_scores)
        trend = np.polyfit(range(len(scores)), scores, 1)[0]  # Linear trend
        
        # Calculate volatility
        volatility = np.std(scores)
        
        # Determine trend direction
        if trend > 5:
            trend_desc = "Improving"
        elif trend < -5:
            trend_desc = "Declining"
        else:
            trend_desc = "Stable"
        
        # Compare to average
        avg_score = np.mean(scores)
        if current_score > avg_score + 10:
            comparison = "significantly above average"
        elif current_score < avg_score - 10:
            comparison = "significantly below average"
        else:
            comparison = "near average"
        
        return {
            'trend': trend_desc.lower(),
            'trend_slope': float(trend),
            'volatility': float(volatility),
            'average_score': float(avg_score),
            'current_vs_average': comparison,
            'description': f"{trend_desc} trend with {comparison} performance (avg: {avg_score:.1f})"
        }
