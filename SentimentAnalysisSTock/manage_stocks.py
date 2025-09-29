#!/usr/bin/env python3
"""
Stock Management System - Add/Remove stocks throughout the application
"""

import os
import sys
import json
from datetime import date, timedelta
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models.models import db, SentimentSummary, Prediction, StockPrice
from backend.config.config import Config

# Company name mappings for display
COMPANY_NAMES = {
    'AAPL': 'Apple Inc.',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'META': 'Meta Platforms Inc.',
    'NFLX': 'Netflix Inc.',
    'TSLA': 'Tesla Inc.',
    'MSFT': 'Microsoft Corp.',
    'NVDA': 'NVIDIA Corp.',
    'IBM': 'IBM Corp.',
    'CRM': 'Salesforce Inc.',
    'ORCL': 'Oracle Corp.',
    'ADBE': 'Adobe Inc.',
    'INTC': 'Intel Corp.',
    'AMD': 'Advanced Micro Devices',
    'BABA': 'Alibaba Group',
    'DIS': 'Walt Disney Co.',
    'NFLX': 'Netflix Inc.',
    'UBER': 'Uber Technologies',
    'LYFT': 'Lyft Inc.',
    'SPOT': 'Spotify Technology',
    'SHOP': 'Shopify Inc.',
    'SQ': 'Block Inc.',
    'PYPL': 'PayPal Holdings',
    'V': 'Visa Inc.',
    'MA': 'Mastercard Inc.',
    'JPM': 'JPMorgan Chase',
    'BAC': 'Bank of America',
    'WFC': 'Wells Fargo',
    'GS': 'Goldman Sachs',
    'MS': 'Morgan Stanley',
    'COIN': 'Coinbase Global',
    'HOOD': 'Robinhood Markets',
    'ZM': 'Zoom Video',
    'TEAM': 'Atlassian Corp.',
    'PLTR': 'Palantir Technologies',
    'SNOW': 'Snowflake Inc.'
}

def add_stocks(symbols):
    """Add new stocks to the application with sample data"""
    print(f"Adding {len(symbols)} new stocks: {', '.join(symbols)}")

    app, _ = create_app()

    with app.app_context():
        today = date.today()
        added_count = 0

        for symbol in symbols:
            symbol = symbol.upper().strip()
            print(f"\n📈 Processing {symbol}...")

            # Create sentiment data for the last 7 days
            sentiment_created = 0
            for i in range(7):
                target_date = today - timedelta(days=i)

                existing = db.session.query(SentimentSummary)\
                    .filter_by(symbol=symbol, date=target_date)\
                    .first()

                if not existing:
                    # Generate realistic sentiment data
                    base_sentiment = np.random.normal(0.4, 0.3)
                    base_sentiment = max(-0.9, min(0.9, base_sentiment))

                    post_count = np.random.randint(2, 12)

                    if base_sentiment > 0.1:
                        positive_count = int(post_count * 0.6)
                        negative_count = int(post_count * 0.2)
                    elif base_sentiment < -0.1:
                        positive_count = int(post_count * 0.2)
                        negative_count = int(post_count * 0.6)
                    else:
                        positive_count = int(post_count * 0.4)
                        negative_count = int(post_count * 0.3)

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
                    sentiment_created += 1

            print(f"  ✅ Created {sentiment_created} sentiment records")

            # Create sample stock price data
            price_created = 0
            base_price = np.random.uniform(50, 500)  # Random base price

            for i in range(7):
                target_date = today - timedelta(days=i)

                existing_price = db.session.query(StockPrice)\
                    .filter_by(symbol=symbol, date=target_date)\
                    .first()

                if not existing_price:
                    # Generate realistic price data
                    daily_change = np.random.normal(0, 0.02)  # 2% daily volatility
                    current_price = base_price * (1 + daily_change * i * 0.1)

                    stock_price = StockPrice(
                        symbol=symbol,
                        date=target_date,
                        open_price=current_price * 0.995,
                        close_price=current_price,
                        high_price=current_price * 1.02,
                        low_price=current_price * 0.98,
                        volume=np.random.randint(1000000, 10000000)
                    )

                    db.session.add(stock_price)
                    price_created += 1

            print(f"  💰 Created {price_created} price records")

            # Create prediction for today
            existing_prediction = db.session.query(Prediction)\
                .filter_by(symbol=symbol, prediction_date=today)\
                .first()

            if not existing_prediction:
                # Get recent sentiment data
                recent_sentiments = db.session.query(SentimentSummary)\
                    .filter(SentimentSummary.symbol == symbol)\
                    .filter(SentimentSummary.date >= today - timedelta(days=7))\
                    .order_by(SentimentSummary.date)\
                    .all()

                if recent_sentiments:
                    sentiment_scores = [s.avg_sentiment for s in recent_sentiments]
                    avg_sentiment = np.mean(sentiment_scores)
                    sentiment_trend = sentiment_scores[-1] - sentiment_scores[0] if len(sentiment_scores) > 1 else 0
                    total_posts = sum(s.post_count for s in recent_sentiments)

                    # Calculate confidence
                    base_confidence = 0.55
                    sentiment_factor = min(0.25, abs(avg_sentiment) * 0.4)
                    trend_factor = min(0.15, abs(sentiment_trend) * 0.3)
                    volume_factor = min(0.05, (total_posts - 3) * 0.02) if total_posts > 3 else 0

                    confidence = base_confidence + sentiment_factor + trend_factor + volume_factor
                    confidence = min(0.95, max(0.52, confidence))

                    # Determine direction
                    if avg_sentiment > 0.1 and sentiment_trend >= -0.1:
                        predicted_direction = 'up'
                    elif avg_sentiment < -0.1 and sentiment_trend <= 0.1:
                        predicted_direction = 'down'
                    else:
                        predicted_direction = 'up' if avg_sentiment >= 0 else 'down'

                    new_prediction = Prediction(
                        symbol=symbol,
                        prediction_date=today,
                        predicted_direction=predicted_direction,
                        confidence=confidence,
                        sentiment_score=avg_sentiment
                    )

                    db.session.add(new_prediction)
                    print(f"  🎯 Created prediction: {predicted_direction.upper()} ({confidence:.1%})")

            added_count += 1

        db.session.commit()
        print(f"\n🎉 Successfully added {added_count} stocks to the database!")
        return True

def update_config_file(new_symbols):
    """Update the config file with new stock symbols"""
    print("\n📝 Updating configuration file...")

    config_path = os.path.join('backend', 'config', 'config.py')

    with open(config_path, 'r') as f:
        content = f.read()

    # Find the STOCKS line and update it
    current_stocks = Config.STOCKS
    all_stocks = list(set(current_stocks + [s.upper() for s in new_symbols]))
    all_stocks.sort()  # Sort alphabetically

    stocks_string = ','.join(all_stocks)

    # Replace the STOCKS line
    import re
    pattern = r"STOCKS = os\.getenv\('STOCKS', '[^']*'\)\.split\(','?\)"
    replacement = f"STOCKS = os.getenv('STOCKS', '{stocks_string}').split(',')"

    content = re.sub(pattern, replacement, content)

    with open(config_path, 'w') as f:
        f.write(content)

    print(f"  ✅ Updated config with {len(all_stocks)} total stocks")
    return all_stocks

def update_html_template(all_stocks):
    """Update the HTML template with new stock options"""
    print("🌐 Updating HTML template...")

    template_path = os.path.join('templates', 'index.html')

    with open(template_path, 'r') as f:
        content = f.read()

    # Generate new options
    options = []
    for symbol in all_stocks:
        company_name = COMPANY_NAMES.get(symbol, symbol)
        options.append(f'                            <option value="{symbol}">{company_name} ({symbol})</option>')

    options_html = '\n'.join(options)

    # Replace the select options
    import re
    pattern = r'(<select id="stock-selector" class="form-select mt-2">\s*)(.*?)(\s*</select>)'
    replacement = f'\\1\n{options_html}\n\\3'

    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(template_path, 'w') as f:
        f.write(content)

    print(f"  ✅ Updated HTML template with {len(all_stocks)} stock options")

def update_javascript_mappings(all_stocks):
    """Update JavaScript company name mappings"""
    print("⚡ Updating JavaScript mappings...")

    js_path = os.path.join('static', 'js', 'dashboard.js')

    with open(js_path, 'r') as f:
        content = f.read()

    # Create mappings for both detailed and short names
    detailed_mapping = {}
    short_mapping = {}

    for symbol in all_stocks:
        detailed_mapping[symbol] = COMPANY_NAMES.get(symbol, f'{symbol} Inc.')
        short_mapping[symbol] = COMPANY_NAMES.get(symbol, symbol).split()[0]  # First word

    # Format as JavaScript objects
    detailed_js = json.dumps(detailed_mapping, indent=16).replace('"', "'")
    short_js = json.dumps(short_mapping, indent=12).replace('"', "'")

    # Replace both company name mappings
    import re

    # Update detailed company names (for metrics)
    pattern1 = r"(const companyNames = )\{[^}]*\};"
    replacement1 = f"\\1{detailed_js};"
    content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)

    # Update short company names (for ticker)
    pattern2 = r"(// Create ticker content with company names and prices\s*const companyNames = )\{[^}]*\};"
    replacement2 = f"\\1{short_js};"
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

    with open(js_path, 'w') as f:
        f.write(content)

    print(f"  ✅ Updated JavaScript with {len(all_stocks)} company mappings")

def main():
    """Main function to add stocks"""
    print("🚀 Stock Management System")
    print("=" * 40)

    # Get user input
    print("Enter stock symbols to add (comma-separated):")
    print("Examples: IBM,CRM,ORCL or UBER,LYFT,SPOT")
    print("Available suggestions: IBM, CRM, ORCL, ADBE, INTC, AMD, BABA, DIS, UBER, LYFT, SPOT, SHOP, SQ, PYPL")

    user_input = input("Stock symbols: ").strip()

    if not user_input:
        print("❌ No stocks provided. Exiting.")
        return

    # Parse input
    new_symbols = [s.strip().upper() for s in user_input.split(',') if s.strip()]

    if not new_symbols:
        print("❌ Invalid input. Exiting.")
        return

    print(f"\n📋 You want to add: {', '.join(new_symbols)}")
    confirm = input("Continue? (y/n): ").lower()

    if confirm != 'y':
        print("❌ Cancelled.")
        return

    try:
        # Step 1: Add to database
        if not add_stocks(new_symbols):
            print("❌ Failed to add stocks to database")
            return

        # Step 2: Update config file
        all_stocks = update_config_file(new_symbols)

        # Step 3: Update HTML template
        update_html_template(all_stocks)

        # Step 4: Update JavaScript
        update_javascript_mappings(all_stocks)

        print(f"\n🎉 SUCCESS! Added {len(new_symbols)} new stocks!")
        print("=" * 50)
        print("📊 Total stocks now tracked:", len(all_stocks))
        print("📝 Stock list:", ', '.join(all_stocks))
        print("\n🔄 Restart your Flask server and refresh browser to see changes!")
        print("   python3 backend/app.py")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()