from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text)
    clean_text = db.Column(db.Text)
    sentiment_score = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False)  # 'reddit', 'news', etc.
    source_url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'title': self.title,
            'content': self.content,
            'sentiment_score': self.sentiment_score,
            'source': self.source,
            'source_url': self.source_url,
            'posted_at': self.posted_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }

class StockPrice(db.Model):
    __tablename__ = 'stock_prices'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('symbol', 'date', name='_symbol_date_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'volume': self.volume,
            'created_at': self.created_at.isoformat()
        }

class SentimentSummary(db.Model):
    __tablename__ = 'sentiment_summary'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    date = db.Column(db.Date, nullable=False)
    avg_sentiment = db.Column(db.Float, nullable=False)
    post_count = db.Column(db.Integer, nullable=False)
    positive_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('symbol', 'date', name='_symbol_date_sentiment_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'date': self.date.isoformat(),
            'avg_sentiment': self.avg_sentiment,
            'post_count': self.post_count,
            'positive_count': self.positive_count,
            'negative_count': self.negative_count,
            'neutral_count': self.neutral_count,
            'created_at': self.created_at.isoformat()
        }

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    prediction_date = db.Column(db.Date, nullable=False)
    predicted_direction = db.Column(db.String(10), nullable=False)  # 'up', 'down'
    confidence = db.Column(db.Float, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=False)
    actual_direction = db.Column(db.String(10))  # filled after actual price movement
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'prediction_date': self.prediction_date.isoformat(),
            'predicted_direction': self.predicted_direction,
            'confidence': self.confidence,
            'sentiment_score': self.sentiment_score,
            'actual_direction': self.actual_direction,
            'created_at': self.created_at.isoformat()
        }

class PredictionVote(db.Model):
    __tablename__ = 'prediction_votes'

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False)
    user_ip = db.Column(db.String(45), nullable=False)  # IPv4/IPv6 address for anonymous voting
    vote_type = db.Column(db.String(10), nullable=False)  # 'agree', 'disagree'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    prediction = db.relationship('Prediction', backref='votes')

    __table_args__ = (db.UniqueConstraint('prediction_id', 'user_ip', name='_prediction_user_vote_uc'),)

    def to_dict(self):
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'user_ip': self.user_ip,
            'vote_type': self.vote_type,
            'created_at': self.created_at.isoformat()
        }