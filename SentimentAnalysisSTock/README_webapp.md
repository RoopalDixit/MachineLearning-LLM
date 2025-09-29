# Stock Sentiment Analysis Web Application

A real-time web application that analyzes sentiment from Reddit posts and news articles to track how public sentiment affects stock prices.

## Features

- **Real-time Sentiment Tracking**: Continuously monitors Reddit and news sources for stock-related content
- **Interactive Dashboard**: Clean, modern interface showing sentiment scores, price correlations, and predictions
- **Multi-source Data**: Combines Reddit posts and news articles for comprehensive sentiment analysis
- **Live Charts**: Real-time visualizations of sentiment vs price correlations
- **Price Predictions**: Basic ML predictions based on sentiment analysis
- **WebSocket Updates**: Live updates without page refresh

## Quick Start

### 1. Set up your environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API credentials

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials:
# - Reddit API credentials (get from https://www.reddit.com/prefs/apps/)
# - News API key (get from https://newsapi.org/)
```

### 3. Initialize the database and collect initial data

```bash
# Run the data pipeline to populate database
python data_pipeline.py
```

### 4. Start the web application

```bash
# Start the Flask server
python backend/app.py
```

### 5. Access the dashboard

Open your browser and go to `http://localhost:5000`

## Project Structure

```
SentimentAnalysisSTock/
├── backend/
│   ├── app.py              # Flask application entry point
│   ├── config/
│   │   └── config.py       # Configuration management
│   ├── models/
│   │   └── models.py       # Database models
│   ├── routes/
│   │   └── api.py          # API endpoints
│   └── utils/
│       ├── sentiment_analyzer.py    # VADER sentiment analysis
│       └── data_collectors.py       # Reddit/News data collection
├── templates/
│   └── index.html          # Dashboard HTML template
├── static/
│   └── js/
│       └── dashboard.js    # Frontend JavaScript
├── data_pipeline.py       # Data collection script
├── requirements.txt       # Python dependencies
└── .env.example           # Environment variables template
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/stocks` | List of tracked stocks |
| `GET /api/sentiment/current` | Current sentiment scores |
| `GET /api/sentiment/history/<symbol>` | Sentiment history for stock |
| `GET /api/prices/current` | Current stock prices |
| `GET /api/prices/history/<symbol>` | Price history for stock |
| `GET /api/correlation/<symbol>` | Sentiment-price correlation data |
| `GET /api/posts/recent` | Recent posts with sentiment |
| `GET /api/predictions/current` | Current price predictions |
| `POST /api/data/refresh` | Trigger data refresh |

## Configuration

The application tracks these stocks by default: `AAPL`, `GOOGL`, `AMZN`, `META`, `NFLX`

You can modify the tracked stocks in your `.env` file:
```
STOCKS=AAPL,GOOGL,AMZN,META,NFLX,TSLA,MSFT
```

## Database Schema

- **posts**: Stores Reddit posts and news articles with sentiment scores
- **stock_prices**: Daily stock price data from Yahoo Finance
- **sentiment_summary**: Daily aggregated sentiment metrics by stock
- **predictions**: ML-based price movement predictions

## Data Pipeline

The `data_pipeline.py` script:
1. Collects Reddit posts from r/stocks subreddit
2. Fetches news articles using News API
3. Analyzes sentiment using VADER
4. Retrieves stock prices from Yahoo Finance
5. Generates daily sentiment summaries
6. Stores everything in SQLite database

Run it periodically (e.g., via cron) to keep data fresh:
```bash
# Run every hour
0 * * * * cd /path/to/project && python data_pipeline.py
```

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-SocketIO
- **Frontend**: Vanilla JavaScript, Bootstrap, Plotly.js
- **Database**: SQLite (easily replaceable with PostgreSQL)
- **APIs**: Reddit (PRAW), News API, Yahoo Finance
- **Sentiment Analysis**: NLTK VADER
- **Real-time**: WebSocket via Socket.IO

## Next Steps / Improvements

1. **Enhanced ML Models**: Replace simple logistic regression with LSTM/transformer models
2. **More Data Sources**: Add Twitter, financial news RSS feeds, SEC filings
3. **Alert System**: Email/SMS notifications for significant sentiment changes
4. **Mobile App**: React Native mobile application
5. **Advanced Charts**: Candlestick charts, technical indicators
6. **User Authentication**: User accounts, custom watchlists
7. **Production Deployment**: Docker, nginx, PostgreSQL setup
8. **Caching**: Redis for API response caching
9. **Testing**: Unit tests, integration tests
10. **Documentation**: API documentation with Swagger

## Troubleshooting

### Common Issues

1. **Missing API credentials**: Ensure `.env` file has valid Reddit and News API keys
2. **NLTK data missing**: The app automatically downloads VADER lexicon, but you may need to run `nltk.download('vader_lexicon')` manually
3. **Port conflicts**: Change the port in `backend/app.py` if 5000 is in use
4. **Database issues**: Delete `sentiment_analysis.db` and run `data_pipeline.py` again to recreate

### Error Messages

- "No module named 'backend'": Make sure you're running from the project root directory
- "Reddit API 403": Check your Reddit API credentials
- "News API quota exceeded": You may have hit the free tier limit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please respect API terms of service and rate limits.