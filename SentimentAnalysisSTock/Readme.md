# Stock Sentiment Analysis from Reddit Posts

## Overview
This Jupyter notebook (`sentiment.ipynb`) performs sentiment analysis on Reddit posts from the r/stocks subreddit for selected tech stocks (AAPL, GOOGL, AMZN, META, NFLX). It uses the PRAW library to scrape posts, cleans the text, applies VADER for sentiment scoring, computes average sentiments, visualizes sentiment vs. stock price for AAPL, and builds a simple logistic regression model to predict price movements based on sentiment.

The analysis aims to explore correlations between social media sentiment and stock price changes. However, the notebook appears incomplete or truncated in the provided document (e.g., stock price data fetching is not shown), and the ML model shows limited performance.

Key libraries used:
- `praw` for Reddit API access
- `pandas` for data manipulation
- `re` for text cleaning
- `nltk` (VADER) for sentiment analysis
- `matplotlib` for visualization
- `sklearn` for machine learning

**Note:** Hardcoded Reddit API credentials are used, which is a security risk. In production, use environment variables or secrets management.

## Data Collection
- **Source:** Reddit subreddit r/stocks.
- **Stocks Analyzed:** AAPL, GOOGL, AMZN, META, NFLX.
- **Method:** Searches for each stock symbol with `sort='new'` and `limit=50` posts per stock.
- **Data Extracted:** Symbol, title, selftext (body), creation timestamp.
- **Output:** Collected 250 posts (50 per stock).
- **Potential Issues:** Limited to recent posts; no historical depth. Reddit API rate limits may apply.

Example code snippet:
```python
import praw

reddit = praw.Reddit(client_id='cVKvSFtYF5Dkfz1-b-Zepg', client_secret='mnh_vsysun3Bqy3gAXoCBCvSqBQFZw', user_agent='stock-sentiment-script')
subreddit = reddit.subreddit('stocks')
posts = []
for stock in ['AAPL', 'GOOGL', 'AMZN', 'META', 'NFLX']:
    for post in subreddit.search(stock, sort='new', limit=50):
        posts.append({'symbol': stock, 'title': post.title, 'selftext': post.selftext, 'created_utc': post.created_utc})
print(f"Collected {len(posts)} posts.")
```

## Data Cleaning
- Converts posts to a Pandas DataFrame.
- Combines title and body into `full_text`.
- Cleans text: Removes URLs, special characters, converts to lowercase.
- **Output Sample:**
  | symbol | clean_text |
  |--------|------------|
  | AAPL   | rstocks daily discussion fundamentals friday ... |
  | AAPL   | apple reports biggest revenue growth since dec... |
  | ...    | ... |

Example code snippet:
```python
df = pd.DataFrame(posts)
df['full_text'] = df['title'].fillna('') + ' ' + df['selftext'].fillna('')
def clean_text(text):
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)  # Remove special chars
    return text.lower().strip()
df['clean_text'] = df['full_text'].apply(clean_text)
```

## Sentiment Analysis
- Uses NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner) for compound sentiment scores (-1 to +1).
- Applies to cleaned text.
- **Output Sample Scores:**
  | symbol | sentiment_score |
  |--------|-----------------|
  | AAPL   | 0.9730          |
  | AAPL   | 0.7096          |
  | ...    | ...             |

- **Average Sentiment per Stock:**
  | symbol | Average Sentiment Score |
  |--------|-------------------------|
  | AAPL   | 0.606312                |
  | AMZN   | 0.441470                |
  | GOOGL  | 0.573006                |
  | META   | 0.609774                |
  | NFLX   | 0.521390                |

- **Observations:** All averages are positive, with META showing the highest sentiment (0.61) and AMZN the lowest (0.44). This suggests generally optimistic discussions, but VADER may not capture sarcasm or financial jargon well.

Example code snippet:
```python
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
df['sentiment_score'] = df['clean_text'].apply(lambda x: sia.polarity_scores(x)['compound'])
avg_sentiment = df.groupby('symbol')['sentiment_score'].mean().reset_index()
```

## Visualization
- Plots average sentiment vs. closing price for AAPL over time.
- Assumes a `merged` DataFrame (not fully shown in the provided notebook; likely merges sentiment with stock price data from an external source like Yahoo Finance).
- Dual-axis plot: Sentiment (blue) on left, Price (green) on right.
- **Output:** A Matplotlib figure showing trends (embedded as base64 PNG in the notebook).

Example code snippet:
```python
import matplotlib.pyplot as plt
stock = 'AAPL'
df_stock = merged[merged['symbol'] == stock]
fig, ax1 = plt.subplots(figsize=(8,4))
ax1.plot(df_stock['date'], df_stock['sentiment_score'], color='tab:blue', marker='o')
ax2 = ax1.twinx()
ax2.plot(df_stock['date'], df_stock['Close'], color='tab:green', marker='s')
plt.title(f'Sentiment & Price for {stock}')
plt.show()
```

- **Observations:** The plot correlates sentiment fluctuations with price changes, but without full data, causality can't be inferred. Sentiment appears volatile.

## Machine Learning: Price Movement Prediction
- **Preprocessing:** Sorts by symbol/date, adds `goes_up` label (1 if next day's price > current, else 0).
- **Features:** Sentiment score only.
- **Model:** Logistic Regression.
- **Train/Test Split:** 67/33.
- **Results:**
  - Accuracy: 0.545 (54.5%)
  - Classification Report:
    ```
    precision    recall  f1-score   support
    0       0.00      0.00      0.00         5
    1       0.55      1.00      0.71         6
    accuracy                           0.55        11
    macro avg       0.27      0.50      0.35        11
    weighted avg       0.30      0.55      0.39        11
    ```
- **Warnings:** Precision ill-defined for class 0 (model predicts all positives, likely due to imbalanced data or weak feature).
- **Observations:** Poor performance; sentiment alone is insufficient for prediction. Add more features (e.g., volume, historical prices) or use advanced models (e.g., LSTM for time series).

Example code snippet:
```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
merged['price_next'] = merged.groupby('symbol')['Close'].shift(-1)
merged['goes_up'] = (merged['price_next'] > merged['Close']).astype(int)
ml_data = merged.dropna(subset=['price_next'])
X = ml_data[['sentiment_score']]
y = ml_data['goes_up']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

## Limitations and Improvements
- **Data Gaps:** Notebook is truncated; stock price fetching (e.g., via `yfinance`) is missing.
- **Bias:** Reddit posts may not represent broad market sentiment; limited to 50 recent posts per stock.
- **Sentiment Tool:** VADER is lexicon-based; consider transformer models (e.g., BERT) for better nuance.
- **ML Issues:** Overly simplistic; handle class imbalance, add features, use time-series validation.
- **Extensions:** Fetch historical data, correlate with more stocks, incorporate Twitter/X data via tools like `x_keyword_search`.

## Conclusion
This notebook demonstrates a basic pipeline for social media sentiment analysis in finance. Average sentiments are positive across stocks, but the predictive model is ineffective, highlighting the challenges of using sentiment alone for stock predictions. Further refinement could yield better insights.

For full execution, ensure Reddit API credentials and missing dependencies (e.g., stock price data) are handled.