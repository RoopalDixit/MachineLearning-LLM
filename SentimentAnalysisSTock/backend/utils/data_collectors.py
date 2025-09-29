import praw
import yfinance as yf
import requests
from datetime import datetime, date, timedelta
from newsapi import NewsApiClient
from backend.config.config import Config
from backend.utils.sentiment_analyzer import SentimentAnalyzer

class RedditCollector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )
        self.sentiment_analyzer = SentimentAnalyzer()

    def collect_posts(self, symbols, limit=50):
        """Collect posts from Reddit for given stock symbols"""
        posts = []
        subreddit = self.reddit.subreddit('stocks')

        for symbol in symbols:
            try:
                for post in subreddit.search(symbol, sort='new', limit=limit):
                    # Analyze sentiment
                    sentiment_data = self.sentiment_analyzer.analyze_post(
                        post.title,
                        post.selftext
                    )

                    post_data = {
                        'symbol': symbol,
                        'title': post.title,
                        'content': post.selftext,
                        'clean_text': sentiment_data['clean_text'],
                        'sentiment_score': sentiment_data['sentiment_score'],
                        'source': 'reddit',
                        'source_url': f"https://reddit.com{post.permalink}",
                        'posted_at': datetime.fromtimestamp(post.created_utc)
                    }
                    posts.append(post_data)

            except Exception as e:
                print(f"Error collecting Reddit posts for {symbol}: {e}")

        return posts

class NewsCollector:
    def __init__(self):
        self.newsapi = NewsApiClient(api_key=Config.NEWS_API_KEY) if Config.NEWS_API_KEY else None
        self.sentiment_analyzer = SentimentAnalyzer()

    def collect_news(self, symbols, days_back=7):
        """Collect news articles for given stock symbols"""
        if not self.newsapi:
            print("News API key not configured")
            return []

        articles = []
        from_date = (date.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        for symbol in symbols:
            try:
                # Search for news about the stock
                company_names = {
                    'AAPL': 'Apple Inc',
                    'GOOGL': 'Google Alphabet',
                    'AMZN': 'Amazon',
                    'META': 'Meta Facebook',
                    'NFLX': 'Netflix'
                }

                query = f"{symbol} OR {company_names.get(symbol, symbol)}"

                news_data = self.newsapi.get_everything(
                    q=query,
                    from_param=from_date,
                    language='en',
                    sort_by='publishedAt',
                    page_size=20
                )

                for article in news_data.get('articles', []):
                    if article['title'] and article['description']:
                        # Analyze sentiment
                        sentiment_data = self.sentiment_analyzer.analyze_post(
                            article['title'],
                            article['description']
                        )

                        article_data = {
                            'symbol': symbol,
                            'title': article['title'],
                            'content': article['description'],
                            'clean_text': sentiment_data['clean_text'],
                            'sentiment_score': sentiment_data['sentiment_score'],
                            'source': 'news',
                            'source_url': article['url'],
                            'posted_at': datetime.fromisoformat(
                                article['publishedAt'].replace('Z', '+00:00')
                            ).replace(tzinfo=None)
                        }
                        articles.append(article_data)

            except Exception as e:
                print(f"Error collecting news for {symbol}: {e}")

        return articles

class StockDataCollector:
    def __init__(self):
        pass

    def collect_stock_prices(self, symbols, period="14d"):
        """Collect stock price data using yfinance"""
        stock_data = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)

                for date_idx, row in hist.iterrows():
                    price_data = {
                        'symbol': symbol,
                        'date': date_idx.date(),
                        'open_price': row['Open'],
                        'high_price': row['High'],
                        'low_price': row['Low'],
                        'close_price': row['Close'],
                        'volume': row['Volume']
                    }
                    stock_data.append(price_data)

            except Exception as e:
                print(f"Error collecting stock data for {symbol}: {e}")

        return stock_data

    def get_current_price(self, symbol):
        """Get current stock price"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception as e:
            print(f"Error getting current price for {symbol}: {e}")
            return None