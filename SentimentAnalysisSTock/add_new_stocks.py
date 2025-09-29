#!/usr/bin/env python3
"""
Add new stocks to the application
"""

import os
import sys
from datetime import date, timedelta
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models.models import db, SentimentSummary, Prediction
from backend.config.config import Config

def main():
    """Add new stocks with data"""
    print("Adding new stocks to the application...")

    app, _ = create_app()

    with app.app_context():
        today = date.today()
        new_stocks = ['TSLA', 'MSFT', 'NVDA']

        for symbol in new_stocks:
            print(f"\nAdding {symbol}...")

            # Create sentiment data for the last 3 days
            for i in range(3):
                target_date = today - timedelta(days=i)

                existing = db.session.query(SentimentSummary)\
                    .filter_by(symbol=symbol, date=target_date)\
                    .first()

                if not existing:
                    # Generate realistic sentiment data
                    base_sentiment = np.random.normal(0.5, 0.25)
                    base_sentiment = max(-0.8, min(0.9, base_sentiment))

                    post_count = np.random.randint(3, 10)

                    positive_count = int(post_count * 0.6) if base_sentiment > 0 else int(post_count * 0.3)
                    negative_count = int(post_count * 0.2) if base_sentiment > 0 else int(post_count * 0.5)
                    neutral_count = post_count - positive_count - negative_count

                    sentiment_summary = SentimentSummary(
                        symbol=symbol,
                        date=target_date,
                        avg_sentiment=base_sentiment,
                        post_count=post_count,
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count
                    )

                    db.session.add(sentiment_summary)
                    print(f"  ✅ Created sentiment data for {target_date}: {base_sentiment:.3f}")

            # Create prediction
            existing_prediction = db.session.query(Prediction)\
                .filter_by(symbol=symbol, prediction_date=today)\
                .first()

            if not existing_prediction:
                # Get the sentiment data we just created
                recent_sentiments = db.session.query(SentimentSummary)\
                    .filter(SentimentSummary.symbol == symbol)\
                    .filter(SentimentSummary.date >= today - timedelta(days=7))\
                    .order_by(SentimentSummary.date)\
                    .all()

                if recent_sentiments:
                    sentiment_scores = [s.avg_sentiment for s in recent_sentiments]
                    avg_sentiment = np.mean(sentiment_scores)

                    # Calculate confidence
                    base_confidence = 0.6
                    sentiment_factor = min(0.3, abs(avg_sentiment) * 0.4)
                    confidence = base_confidence + sentiment_factor
                    confidence = min(0.95, max(0.55, confidence))

                    predicted_direction = 'up' if avg_sentiment > 0 else 'down'

                    new_prediction = Prediction(
                        symbol=symbol,
                        prediction_date=today,
                        predicted_direction=predicted_direction,
                        confidence=confidence,
                        sentiment_score=avg_sentiment
                    )

                    db.session.add(new_prediction)
                    print(f"  🎯 Created prediction: {predicted_direction.upper()} ({confidence:.1%})")

        db.session.commit()
        print("\n🎉 All new stocks added successfully!")
        print("🌐 Refresh your browser to see all 8 stocks!")

if __name__ == "__main__":
    main()