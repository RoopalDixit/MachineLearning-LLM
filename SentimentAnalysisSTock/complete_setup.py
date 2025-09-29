#!/usr/bin/env python3
"""
Complete setup for all 15 stocks - adds missing data and sample posts
"""

import os
import sys
from datetime import date, timedelta, datetime
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models.models import db, SentimentSummary, Prediction, StockPrice, Post

# All 15 stocks we want
ALL_STOCKS = ['AAPL', 'GOOGL', 'AMZN', 'META', 'NFLX', 'TSLA', 'MSFT', 'NVDA', 'IBM', 'CRM', 'ORCL', 'ADBE', 'INTC', 'AMD', 'UBER', 'PYPL', 'SPOT', 'SQ']

# Sample post titles and content
SAMPLE_POSTS = [
    ("Strong quarterly earnings beat expectations", "Company reported revenue growth of 15% year-over-year with strong fundamentals."),
    ("New product launch driving investor sentiment", "Latest product announcement has generated significant market buzz and positive analyst coverage."),
    ("Analyst upgrade boosts stock confidence", "Major investment firm raised price target citing strong competitive position."),
    ("Market volatility affects tech sector broadly", "Broader market trends impacting technology stocks across the board today."),
    ("CEO announces strategic partnership deal", "New collaboration expected to drive revenue growth in coming quarters."),
    ("Insider buying signals confidence", "Several executives purchased additional shares, indicating strong internal confidence."),
    ("Revenue guidance raised for next quarter", "Management increased forward guidance based on strong demand trends."),
    ("New market expansion announced", "Company entering new geographic markets with significant growth potential."),
    ("Innovation breakthrough in core technology", "Research and development team achieved major technological milestone."),
    ("Supply chain improvements boost margins", "Operational efficiency gains contributing to improved profitability metrics.")
]

def create_complete_stock_data():
    """Create comprehensive data for all 15 stocks"""
    print("🚀 Setting up complete data for all 15 stocks...")

    app, _ = create_app()

    with app.app_context():
        today = date.today()

        for stock in ALL_STOCKS:
            print(f"\n📈 Setting up {stock}...")

            # 1. Create sentiment summaries (7 days)
            sentiment_count = 0
            for i in range(7):
                target_date = today - timedelta(days=i)

                existing = db.session.query(SentimentSummary)\
                    .filter_by(symbol=stock, date=target_date)\
                    .first()

                if not existing:
                    base_sentiment = np.random.normal(0.4, 0.3)
                    base_sentiment = max(-0.85, min(0.85, base_sentiment))
                    post_count = np.random.randint(2, 12)

                    if base_sentiment > 0.1:
                        positive_count = int(post_count * 0.65)
                        negative_count = int(post_count * 0.15)
                    elif base_sentiment < -0.1:
                        positive_count = int(post_count * 0.15)
                        negative_count = int(post_count * 0.65)
                    else:
                        positive_count = int(post_count * 0.45)
                        negative_count = int(post_count * 0.25)

                    neutral_count = post_count - positive_count - negative_count

                    sentiment_summary = SentimentSummary(
                        symbol=stock,
                        date=target_date,
                        avg_sentiment=base_sentiment,
                        post_count=post_count,
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count
                    )

                    db.session.add(sentiment_summary)
                    sentiment_count += 1

            # 2. Create stock prices (7 days)
            price_count = 0
            base_price = np.random.uniform(50, 400)

            for i in range(7):
                target_date = today - timedelta(days=i)

                existing_price = db.session.query(StockPrice)\
                    .filter_by(symbol=stock, date=target_date)\
                    .first()

                if not existing_price:
                    daily_change = np.random.normal(0, 0.025)
                    current_price = base_price * (1 + daily_change * i * 0.1)

                    stock_price = StockPrice(
                        symbol=stock,
                        date=target_date,
                        open_price=current_price * 0.998,
                        close_price=current_price,
                        high_price=current_price * 1.015,
                        low_price=current_price * 0.985,
                        volume=np.random.randint(500000, 8000000)
                    )

                    db.session.add(stock_price)
                    price_count += 1

            # 3. Create sample posts (3-5 per stock)
            post_count = 0
            num_posts = np.random.randint(3, 6)

            for j in range(num_posts):
                post_date = today - timedelta(days=np.random.randint(0, 3))
                title, content = SAMPLE_POSTS[np.random.randint(0, len(SAMPLE_POSTS))]
                title = f"{stock}: {title}"

                sentiment_score = np.random.normal(0.3, 0.4)
                sentiment_score = max(-0.9, min(0.9, sentiment_score))

                post = Post(
                    symbol=stock,
                    title=title,
                    content=content,
                    clean_text=content,
                    sentiment_score=sentiment_score,
                    source='reddit',
                    source_url=f'https://reddit.com/r/stocks/{stock.lower()}_{j}',
                    posted_at=datetime.combine(post_date, datetime.min.time())
                )

                db.session.add(post)
                post_count += 1

            # 4. Create/update prediction for today
            existing_prediction = db.session.query(Prediction)\
                .filter_by(symbol=stock, prediction_date=today)\
                .first()

            if not existing_prediction:
                # Get sentiment data for prediction
                recent_sentiments = db.session.query(SentimentSummary)\
                    .filter(SentimentSummary.symbol == stock)\
                    .filter(SentimentSummary.date >= today - timedelta(days=7))\
                    .order_by(SentimentSummary.date)\
                    .all()

                if recent_sentiments:
                    sentiment_scores = [s.avg_sentiment for s in recent_sentiments]
                    avg_sentiment = np.mean(sentiment_scores)

                    confidence = 0.58 + abs(avg_sentiment) * 0.35 + np.random.normal(0, 0.05)
                    confidence = min(0.93, max(0.54, confidence))

                    predicted_direction = 'up' if avg_sentiment > -0.05 else 'down'

                    new_prediction = Prediction(
                        symbol=stock,
                        prediction_date=today,
                        predicted_direction=predicted_direction,
                        confidence=confidence,
                        sentiment_score=avg_sentiment
                    )

                    db.session.add(new_prediction)
                    print(f"  🎯 Prediction: {predicted_direction.upper()} ({confidence:.1%})")

            print(f"  ✅ Added {sentiment_count} sentiments, {price_count} prices, {post_count} posts")

        # Commit all changes
        db.session.commit()

        print(f"\n🎉 Complete setup finished for all {len(ALL_STOCKS)} stocks!")

        # Verify the data
        print("\n📊 Verification:")
        for stock in ALL_STOCKS:
            sentiment_count = db.session.query(SentimentSummary).filter_by(symbol=stock).count()
            price_count = db.session.query(StockPrice).filter_by(symbol=stock).count()
            post_count = db.session.query(Post).filter_by(symbol=stock).count()
            prediction = db.session.query(Prediction).filter_by(symbol=stock, prediction_date=today).first()

            pred_str = f"{prediction.predicted_direction.upper()} ({prediction.confidence:.1%})" if prediction else "None"
            print(f"  {stock}: {sentiment_count}S, {price_count}P, {post_count}Posts, {pred_str}")

if __name__ == "__main__":
    create_complete_stock_data()