#!/usr/bin/env python3
"""
Generate sample predictions for today to demonstrate voting feature
"""

import sys
import os
import random
from datetime import date

# Add backend to path
sys.path.append('backend')

from backend.app import create_app
from backend.models.models import db, Prediction
from backend.config.config import Config

def generate_sample_predictions():
    """Generate sample predictions for today"""
    print("Generating sample predictions for today...")

    app, _ = create_app()

    with app.app_context():
        today = date.today()

        # Clear existing predictions for today
        existing = Prediction.query.filter_by(prediction_date=today).all()
        for pred in existing:
            db.session.delete(pred)

        # Generate predictions for each stock
        predictions = []
        for symbol in Config.STOCKS[:6]:  # Generate for first 6 stocks
            # Random prediction
            direction = random.choice(['up', 'down'])
            confidence = round(random.uniform(0.6, 0.9), 2)
            sentiment_score = round(random.uniform(-0.5, 0.5), 3)

            prediction = Prediction(
                symbol=symbol,
                prediction_date=today,
                predicted_direction=direction,
                confidence=confidence,
                sentiment_score=sentiment_score
            )

            predictions.append(prediction)
            db.session.add(prediction)
            print(f"✅ Created prediction for {symbol}: {direction} (confidence: {confidence})")

        db.session.commit()
        print(f"✅ Generated {len(predictions)} predictions for {today}")

        # Verify predictions were created
        created_predictions = Prediction.query.filter_by(prediction_date=today).all()
        print(f"✅ Verified: {len(created_predictions)} predictions in database")

if __name__ == "__main__":
    generate_sample_predictions()