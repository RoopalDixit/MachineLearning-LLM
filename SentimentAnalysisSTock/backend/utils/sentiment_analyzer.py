import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon if not already present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def clean_text(self, text):
        """Clean text by removing URLs and special characters"""
        if not text:
            return ""

        # Remove URLs
        text = re.sub(r"http\S+", "", text)
        # Remove special characters, keep only alphanumeric and spaces
        text = re.sub(r"[^A-Za-z0-9\s]", "", text)
        # Convert to lowercase and strip whitespace
        return text.lower().strip()

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text using VADER
        Returns compound score between -1 (negative) and 1 (positive)
        """
        if not text:
            return 0.0

        clean_text = self.clean_text(text)
        if not clean_text:
            return 0.0

        scores = self.analyzer.polarity_scores(clean_text)
        return scores['compound']

    def categorize_sentiment(self, score):
        """Categorize sentiment score into positive, negative, or neutral"""
        if score >= 0.05:
            return 'positive'
        elif score <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    def analyze_post(self, title, content=""):
        """Analyze sentiment of a post (title + content)"""
        full_text = f"{title} {content}".strip()
        score = self.analyze_sentiment(full_text)
        category = self.categorize_sentiment(score)

        return {
            'sentiment_score': score,
            'sentiment_category': category,
            'clean_text': self.clean_text(full_text)
        }