#!/usr/bin/env python3
"""
Add popular stocks automatically
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

# Popular stocks to add with their company names
POPULAR_STOCKS = {
    'IBM': 'IBM Corp.',
    'CRM': 'Salesforce Inc.',
    'ORCL': 'Oracle Corp.',
    'ADBE': 'Adobe Inc.',
    'INTC': 'Intel Corp.',
    'AMD': 'Advanced Micro Devices',
    'UBER': 'Uber Technologies',
    'SPOT': 'Spotify Technology',
    'SQ': 'Block Inc.',
    'PYPL': 'PayPal Holdings'
}

def add_stocks_to_db(symbols):
    """Add stocks with sample data to database"""
    print(f"Adding {len(symbols)} stocks to database...")

    app, _ = create_app()

    with app.app_context():
        today = date.today()

        for symbol in symbols:
            print(f"\n📈 Adding {symbol} ({POPULAR_STOCKS[symbol]})...")

            # Create sentiment data for the last 7 days
            for i in range(7):
                target_date = today - timedelta(days=i)

                existing = db.session.query(SentimentSummary)\
                    .filter_by(symbol=symbol, date=target_date)\
                    .first()

                if not existing:
                    base_sentiment = np.random.normal(0.3, 0.35)
                    base_sentiment = max(-0.85, min(0.85, base_sentiment))
                    post_count = np.random.randint(3, 15)

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
                        symbol=symbol,
                        date=target_date,
                        avg_sentiment=base_sentiment,
                        post_count=post_count,
                        positive_count=positive_count,
                        negative_count=negative_count,
                        neutral_count=neutral_count
                    )
                    db.session.add(sentiment_summary)

            # Create sample stock price data
            base_price = np.random.uniform(30, 400)
            for i in range(7):
                target_date = today - timedelta(days=i)

                existing_price = db.session.query(StockPrice)\
                    .filter_by(symbol=symbol, date=target_date)\
                    .first()

                if not existing_price:
                    daily_change = np.random.normal(0, 0.025)
                    current_price = base_price * (1 + daily_change * i * 0.1)

                    stock_price = StockPrice(
                        symbol=symbol,
                        date=target_date,
                        open_price=current_price * 0.998,
                        close_price=current_price,
                        high_price=current_price * 1.015,
                        low_price=current_price * 0.985,
                        volume=np.random.randint(500000, 8000000)
                    )
                    db.session.add(stock_price)

            # Create prediction
            existing_prediction = db.session.query(Prediction)\
                .filter_by(symbol=symbol, prediction_date=today)\
                .first()

            if not existing_prediction:
                recent_sentiments = db.session.query(SentimentSummary)\
                    .filter(SentimentSummary.symbol == symbol)\
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
                        symbol=symbol,
                        prediction_date=today,
                        predicted_direction=predicted_direction,
                        confidence=confidence,
                        sentiment_score=avg_sentiment
                    )
                    db.session.add(new_prediction)
                    print(f"  🎯 Prediction: {predicted_direction.upper()} ({confidence:.1%})")

        db.session.commit()
        print(f"\n✅ Database updated with {len(symbols)} new stocks!")

def update_config_file():
    """Update config file with all stocks"""
    print("📝 Updating config file...")

    config_path = os.path.join('backend', 'config', 'config.py')

    current_stocks = Config.STOCKS
    new_stocks = list(POPULAR_STOCKS.keys())
    all_stocks = list(set(current_stocks + new_stocks))
    all_stocks.sort()

    stocks_string = ','.join(all_stocks)

    with open(config_path, 'r') as f:
        content = f.read()

    import re
    pattern = r"STOCKS = os\.getenv\('STOCKS', '[^']*'\)\.split\(','?\)"
    replacement = f"STOCKS = os.getenv('STOCKS', '{stocks_string}').split(',')"
    content = re.sub(pattern, replacement, content)

    with open(config_path, 'w') as f:
        f.write(content)

    print(f"  ✅ Config updated with {len(all_stocks)} total stocks")
    return all_stocks

def update_html_template(all_stocks):
    """Update HTML dropdown with all stocks"""
    print("🌐 Updating HTML template...")

    template_path = os.path.join('templates', 'index.html')

    # All company names
    all_companies = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NFLX': 'Netflix Inc.',
        'TSLA': 'Tesla Inc.',
        'MSFT': 'Microsoft Corp.',
        'NVDA': 'NVIDIA Corp.',
        **POPULAR_STOCKS
    }

    options = []
    for symbol in all_stocks:
        company_name = all_companies.get(symbol, symbol)
        options.append(f'                            <option value="{symbol}">{company_name} ({symbol})</option>')

    options_html = '\n'.join(options)

    with open(template_path, 'r') as f:
        content = f.read()

    import re
    pattern = r'(<select id="stock-selector" class="form-select mt-2">\s*)(.*?)(\s*</select>)'
    replacement = f'\\1\n{options_html}\n\\3'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open(template_path, 'w') as f:
        f.write(content)

    print(f"  ✅ HTML updated with {len(all_stocks)} stock options")

def update_javascript(all_stocks):
    """Update JavaScript company mappings"""
    print("⚡ Updating JavaScript...")

    js_path = os.path.join('static', 'js', 'dashboard.js')

    # All company mappings
    all_companies = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'META': 'Meta Platforms Inc.',
        'NFLX': 'Netflix Inc.',
        'TSLA': 'Tesla Inc.',
        'MSFT': 'Microsoft Corp.',
        'NVDA': 'NVIDIA Corp.',
        **POPULAR_STOCKS
    }

    # Create mappings for metrics and ticker
    detailed_mapping = {symbol: all_companies.get(symbol, f'{symbol} Inc.') for symbol in all_stocks}
    short_mapping = {symbol: all_companies.get(symbol, symbol).split()[0] for symbol in all_stocks}

    with open(js_path, 'r') as f:
        content = f.read()

    # Format as JavaScript
    detailed_js = json.dumps(detailed_mapping, indent=16).replace('"', "'")
    short_js = json.dumps(short_mapping, indent=12).replace('"', "'")

    import re

    # Update both company name mappings
    content = re.sub(
        r"(const companyNames = )\{[^}]*\};",
        f"\\1{detailed_js};",
        content,
        flags=re.DOTALL
    )

    # Update ticker mapping (second occurrence)
    parts = content.split("const companyNames = ")
    if len(parts) >= 3:  # First part + at least 2 occurrences
        # Replace the second occurrence
        second_part = parts[2]
        updated_second = re.sub(
            r"\{[^}]*\};",
            f"{short_js};",
            second_part,
            count=1,
            flags=re.DOTALL
        )
        content = parts[0] + "const companyNames = " + parts[1] + "const companyNames = " + updated_second

    with open(js_path, 'w') as f:
        f.write(content)

    print(f"  ✅ JavaScript updated with {len(all_stocks)} companies")

def main():
    """Add popular stocks to the application"""
    print("🚀 Adding Popular Stocks to Application")
    print("=" * 50)

    stock_symbols = list(POPULAR_STOCKS.keys())

    print("📊 Adding these stocks:")
    for symbol, name in POPULAR_STOCKS.items():
        print(f"  • {symbol} - {name}")

    try:
        # Add to database
        add_stocks_to_db(stock_symbols)

        # Update configuration
        all_stocks = update_config_file()

        # Update HTML template
        update_html_template(all_stocks)

        # Update JavaScript
        update_javascript(all_stocks)

        print("\n🎉 SUCCESS! Popular stocks added!")
        print("=" * 50)
        print(f"📈 Total stocks now: {len(all_stocks)}")
        print(f"📝 All stocks: {', '.join(sorted(all_stocks))}")
        print("\n🔄 Restart your Flask server to see changes:")
        print("   Kill current server and run: python3 backend/app.py")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()