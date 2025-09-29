import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///sentiment_analysis.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Reddit API settings
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'stock-sentiment-webapp')

    # News API settings
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')

    # Redis settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    # Application settings
    STOCKS = os.getenv('STOCKS', 'AAPL,GOOGL,AMZN,META,NFLX,TSLA,MSFT,NVDA,IBM,CRM,ORCL,ADBE,INTC,AMD,UBER,PYPL,SPOT,SQ').split(',')
    UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', 300))  # 5 minutes

    # CORS settings
    CORS_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://localhost:3000', 'http://127.0.0.1:3000']