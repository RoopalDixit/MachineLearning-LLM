#!/usr/bin/env python3
"""
Data pipeline for collecting and processing stock sentiment data
Run this script to populate your database with initial data
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models.models import db, Post, StockPrice, SentimentSummary
from backend.utils.data_collectors import RedditCollector, NewsCollector, StockDataCollector
from backend.utils.sentiment_analyzer import SentimentAnalyzer
from backend.config.config import Config

def collect_and_store_posts():
    """Collect posts from Reddit and News APIs and store in database"""
    print("Collecting Reddit posts...")
    reddit_collector = RedditCollector()
    reddit_posts = reddit_collector.collect_posts(Config.STOCKS, limit=50)

    print("Collecting news articles...")
    news_collector = NewsCollector()
    news_posts = news_collector.collect_news(Config.STOCKS, days_back=7)

    all_posts = reddit_posts + news_posts
    print(f"Collected {len(all_posts)} posts total")

    # Store posts in database
    for post_data in all_posts:
        existing_post = Post.query.filter_by(
            title=post_data['title'],
            source=post_data['source'],
            posted_at=post_data['posted_at']
        ).first()

        if not existing_post:
            post = Post(**post_data)
            db.session.add(post)

    db.session.commit()
    print("Posts stored in database")

def collect_and_store_stock_prices():
    """Collect stock price data and store in database"""
    print("Collecting stock price data...")
    stock_collector = StockDataCollector()
    stock_data = stock_collector.collect_stock_prices(Config.STOCKS, period="30d")

    print(f"Collected price data for {len(stock_data)} data points")

    # Store stock prices in database
    for price_data in stock_data:
        existing_price = StockPrice.query.filter_by(
            symbol=price_data['symbol'],
            date=price_data['date']
        ).first()

        if not existing_price:
            price = StockPrice(**price_data)
            db.session.add(price)

    db.session.commit()
    print("Stock prices stored in database")

def generate_sentiment_summaries():
    """Generate daily sentiment summaries for each stock"""
    print("Generating sentiment summaries...")

    # Get date range for last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    for symbol in Config.STOCKS:
        for single_date in [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]:
            # Get posts for this symbol and date
            posts = Post.query.filter(
                Post.symbol == symbol,
                db.func.date(Post.posted_at) == single_date
            ).all()

            if posts:
                # Calculate sentiment metrics
                sentiment_scores = [p.sentiment_score for p in posts]
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                post_count = len(posts)

                positive_count = sum(1 for s in sentiment_scores if s > 0.05)
                negative_count = sum(1 for s in sentiment_scores if s < -0.05)
                neutral_count = post_count - positive_count - negative_count

                # Check if summary already exists
                existing_summary = SentimentSummary.query.filter_by(
                    symbol=symbol,
                    date=single_date
                ).first()

                if existing_summary:
                    # Update existing summary
                    existing_summary.avg_sentiment = avg_sentiment
                    existing_summary.post_count = post_count
                    existing_summary.positive_count = positive_count
                    existing_summary.negative_count = negative_count
                    existing_summary.neutral_count = neutral_count
                else:
                    # Create new summary
                    summary = SentimentSummary(
                        symbol=symbol,
                        date=single_date,
                        avg_sentiment=avg_sentiment,
                        post_count=post_count,
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count
                    )
                    db.session.add(summary)

    db.session.commit()
    print("Sentiment summaries generated")

def main():
    """Main function to run the data pipeline"""
    print("Starting data pipeline...")
    print(f"Tracking stocks: {', '.join(Config.STOCKS)}")

    # Create Flask app context
    app, _ = create_app()

    with app.app_context():
        # Ensure database tables exist
        db.create_all()

        try:
            # Step 1: Collect and store posts
            collect_and_store_posts()

            # Step 2: Collect and store stock prices
            collect_and_store_stock_prices()

            # Step 3: Generate sentiment summaries
            generate_sentiment_summaries()

            print("Data pipeline completed successfully!")

            # Print summary statistics
            total_posts = Post.query.count()
            total_prices = StockPrice.query.count()
            total_summaries = SentimentSummary.query.count()

            print(f"\nDatabase Summary:")
            print(f"- Total posts: {total_posts}")
            print(f"- Total price records: {total_prices}")
            print(f"- Total sentiment summaries: {total_summaries}")

        except Exception as e:
            print(f"Error in data pipeline: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    main()