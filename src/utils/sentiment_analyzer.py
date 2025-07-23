from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Union
import logging

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
    
    def analyze(self, text: str) -> float:
        """
        Analyze the sentiment of given text and return a compound score
        between -1 (negative) and 1 (positive)
        """
        try:
            sentiment_dict = self.analyzer.polarity_scores(text)
            return sentiment_dict['compound']
        except Exception as e:
            logging.error(f"Error in sentiment analysis: {e}")
            return 0.0  # Neutral sentiment in case of error

    def get_detailed_sentiment(self, text: str) -> Dict[str, Union[float, str]]:
        """
        Get detailed sentiment analysis including positive, negative, and neutral scores
        """
        try:
            scores = self.analyzer.polarity_scores(text)
            
            # Determine overall sentiment
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'compound': scores['compound'],
                'overall': sentiment
            }
        except Exception as e:
            logging.error(f"Error in detailed sentiment analysis: {e}")
            return {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'compound': 0.0,
                'overall': 'neutral'
            }

# Create singleton instance
sentiment_analyzer = SentimentAnalyzer()

def analyze_sentiment(text: str) -> float:
    """
    Helper function to quickly get sentiment score
    """
    return sentiment_analyzer.analyze(text)
