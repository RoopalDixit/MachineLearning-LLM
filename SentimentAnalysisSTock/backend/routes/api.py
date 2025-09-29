from flask import Blueprint, jsonify, request
from datetime import date, datetime, timedelta
from sqlalchemy import func
from backend.models.models import db, Post, StockPrice, SentimentSummary, Prediction, PredictionVote
from backend.utils.data_collectors import RedditCollector, NewsCollector, StockDataCollector
from backend.config.config import Config

api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@api.route('/stocks', methods=['GET'])
def get_stocks():
    """Get list of tracked stocks"""
    return jsonify({'stocks': Config.STOCKS})

@api.route('/sentiment/current', methods=['GET'])
def get_current_sentiment():
    """Get current sentiment scores for all stocks"""
    try:
        # Get latest sentiment summary for each stock
        latest_sentiments = []

        for stock in Config.STOCKS:
            latest = db.session.query(SentimentSummary)\
                .filter_by(symbol=stock)\
                .order_by(SentimentSummary.date.desc())\
                .first()

            if latest:
                latest_sentiments.append(latest.to_dict())
            else:
                # If no data, return neutral sentiment
                latest_sentiments.append({
                    'symbol': stock,
                    'avg_sentiment': 0.0,
                    'post_count': 0,
                    'date': date.today().isoformat()
                })

        return jsonify({'sentiment_data': latest_sentiments})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/sentiment/history/<symbol>', methods=['GET'])
def get_sentiment_history(symbol):
    """Get sentiment history for a specific stock"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)

        sentiment_history = db.session.query(SentimentSummary)\
            .filter(SentimentSummary.symbol == symbol.upper())\
            .filter(SentimentSummary.date >= start_date)\
            .order_by(SentimentSummary.date)\
            .all()

        return jsonify({
            'symbol': symbol.upper(),
            'history': [s.to_dict() for s in sentiment_history]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/prices/current', methods=['GET'])
def get_current_prices():
    """Get current stock prices from database (most recent)"""
    try:
        current_prices = []

        for stock in Config.STOCKS:
            # Get most recent price from database
            latest_price = db.session.query(StockPrice)\
                .filter_by(symbol=stock)\
                .order_by(StockPrice.date.desc())\
                .first()

            if latest_price:
                current_prices.append({
                    'symbol': stock,
                    'current_price': latest_price.close_price,
                    'timestamp': datetime.utcnow().isoformat(),
                    'date': latest_price.date.isoformat()
                })

        return jsonify({'prices': current_prices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/prices/history/<symbol>', methods=['GET'])
def get_price_history(symbol):
    """Get price history for a specific stock"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)

        price_history = db.session.query(StockPrice)\
            .filter(StockPrice.symbol == symbol.upper())\
            .filter(StockPrice.date >= start_date)\
            .order_by(StockPrice.date)\
            .all()

        return jsonify({
            'symbol': symbol.upper(),
            'history': [p.to_dict() for p in price_history]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/correlation/<symbol>', methods=['GET'])
def get_correlation_data(symbol):
    """Get correlation data between sentiment and price for a stock"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = date.today() - timedelta(days=days)

        # Get sentiment data
        sentiment_data = db.session.query(SentimentSummary)\
            .filter(SentimentSummary.symbol == symbol.upper())\
            .filter(SentimentSummary.date >= start_date)\
            .order_by(SentimentSummary.date)\
            .all()

        # Get price data
        price_data = db.session.query(StockPrice)\
            .filter(StockPrice.symbol == symbol.upper())\
            .filter(StockPrice.date >= start_date)\
            .order_by(StockPrice.date)\
            .all()

        # Combine data by date
        correlation_data = []
        sentiment_dict = {s.date: s for s in sentiment_data}
        price_dict = {p.date: p for p in price_data}

        for date_key in sorted(set(sentiment_dict.keys()) & set(price_dict.keys())):
            correlation_data.append({
                'date': date_key.isoformat(),
                'sentiment_score': sentiment_dict[date_key].avg_sentiment,
                'close_price': price_dict[date_key].close_price,
                'post_count': sentiment_dict[date_key].post_count
            })

        return jsonify({
            'symbol': symbol.upper(),
            'correlation_data': correlation_data
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/posts/recent', methods=['GET'])
def get_recent_posts():
    """Get recent posts with sentiment scores"""
    try:
        limit = request.args.get('limit', 50, type=int)
        symbol = request.args.get('symbol')

        query = db.session.query(Post).order_by(Post.posted_at.desc())

        if symbol:
            query = query.filter(Post.symbol == symbol.upper())

        posts = query.limit(limit).all()

        return jsonify({
            'posts': [p.to_dict() for p in posts]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/predictions/current', methods=['GET'])
def get_current_predictions():
    """Get current predictions for all stocks"""
    try:
        predictions = []
        today = date.today()

        for stock in Config.STOCKS:
            prediction = db.session.query(Prediction)\
                .filter_by(symbol=stock)\
                .filter_by(prediction_date=today)\
                .first()

            if prediction:
                predictions.append(prediction.to_dict())

        return jsonify({'predictions': predictions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/data/refresh', methods=['POST'])
def refresh_data():
    """Manually trigger data refresh"""
    try:
        # This would trigger background tasks in a production environment
        # For now, we'll return a success message
        return jsonify({
            'message': 'Data refresh initiated',
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary across all stocks"""
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)

        # Get total posts in last 7 days
        total_posts = db.session.query(func.count(Post.id))\
            .filter(Post.posted_at >= week_ago)\
            .scalar()

        # Get average sentiment by stock
        avg_sentiments = db.session.query(
            SentimentSummary.symbol,
            func.avg(SentimentSummary.avg_sentiment).label('avg_sentiment')
        )\
        .filter(SentimentSummary.date >= week_ago)\
        .group_by(SentimentSummary.symbol)\
        .all()

        summary_data = {
            'total_posts_7d': total_posts,
            'average_sentiments': [
                {'symbol': s.symbol, 'avg_sentiment': float(s.avg_sentiment)}
                for s in avg_sentiments
            ],
            'period': f"{week_ago.isoformat()} to {today.isoformat()}"
        }

        return jsonify(summary_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Prediction Voting Endpoints
@api.route('/predictions/<int:prediction_id>/vote', methods=['POST'])
def vote_on_prediction(prediction_id):
    """Vote on a prediction (agree/disagree)"""
    try:
        data = request.get_json()
        vote_type = data.get('vote_type')  # 'agree' or 'disagree'

        if vote_type not in ['agree', 'disagree']:
            return jsonify({'error': 'Vote type must be "agree" or "disagree"'}), 400

        # Get user IP for anonymous voting
        user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        # Check if prediction exists
        prediction = db.session.query(Prediction).filter_by(id=prediction_id).first()
        if not prediction:
            return jsonify({'error': 'Prediction not found'}), 404

        # Check if user already voted
        existing_vote = db.session.query(PredictionVote)\
            .filter_by(prediction_id=prediction_id, user_ip=user_ip)\
            .first()

        if existing_vote:
            # Update existing vote
            existing_vote.vote_type = vote_type
            message = 'Vote updated successfully'
        else:
            # Create new vote
            new_vote = PredictionVote(
                prediction_id=prediction_id,
                user_ip=user_ip,
                vote_type=vote_type
            )
            db.session.add(new_vote)
            message = 'Vote recorded successfully'

        db.session.commit()

        # Get updated vote counts
        vote_stats = get_prediction_vote_stats(prediction_id)

        return jsonify({
            'message': message,
            'vote_stats': vote_stats
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/predictions/<int:prediction_id>/votes', methods=['GET'])
def get_prediction_votes(prediction_id):
    """Get vote statistics for a prediction"""
    try:
        vote_stats = get_prediction_vote_stats(prediction_id)
        return jsonify(vote_stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/predictions/current/with-votes', methods=['GET'])
def get_predictions_with_votes():
    """Get current predictions with vote statistics"""
    try:
        predictions = []
        today = date.today()

        for stock in Config.STOCKS:
            prediction = db.session.query(Prediction)\
                .filter_by(symbol=stock)\
                .filter_by(prediction_date=today)\
                .first()

            if prediction:
                pred_dict = prediction.to_dict()
                pred_dict['vote_stats'] = get_prediction_vote_stats(prediction.id)
                predictions.append(pred_dict)

        return jsonify({'predictions': predictions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_prediction_vote_stats(prediction_id):
    """Helper function to get vote statistics for a prediction"""
    votes = db.session.query(PredictionVote)\
        .filter_by(prediction_id=prediction_id)\
        .all()

    agree_count = sum(1 for vote in votes if vote.vote_type == 'agree')
    disagree_count = sum(1 for vote in votes if vote.vote_type == 'disagree')
    total_votes = len(votes)

    agreement_percentage = (agree_count / total_votes * 100) if total_votes > 0 else 0

    return {
        'agree_count': agree_count,
        'disagree_count': disagree_count,
        'total_votes': total_votes,
        'agreement_percentage': round(agreement_percentage, 1)
    }

# Stock Comparison Endpoints
@api.route('/compare/stocks', methods=['POST'])
def compare_stocks():
    """Compare sentiment and price data for multiple stocks"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        days = data.get('days', 30)

        if not symbols or len(symbols) < 2:
            return jsonify({'error': 'At least 2 stocks required for comparison'}), 400

        if len(symbols) > 4:
            return jsonify({'error': 'Maximum 4 stocks can be compared at once'}), 400

        start_date = date.today() - timedelta(days=days)
        comparison_data = []

        for symbol in symbols:
            symbol = symbol.upper()

            # Get sentiment data
            sentiment_data = db.session.query(SentimentSummary)\
                .filter(SentimentSummary.symbol == symbol)\
                .filter(SentimentSummary.date >= start_date)\
                .order_by(SentimentSummary.date)\
                .all()

            # Get price data
            price_data = db.session.query(StockPrice)\
                .filter(StockPrice.symbol == symbol)\
                .filter(StockPrice.date >= start_date)\
                .order_by(StockPrice.date)\
                .all()

            # Get current prediction
            current_prediction = db.session.query(Prediction)\
                .filter_by(symbol=symbol)\
                .filter_by(prediction_date=date.today())\
                .first()

            # Calculate metrics
            latest_sentiment = sentiment_data[-1] if sentiment_data else None
            latest_price = price_data[-1] if price_data else None

            # Calculate price change
            price_change = 0
            price_change_percent = 0
            if len(price_data) >= 2:
                first_price = price_data[0].close_price
                last_price = price_data[-1].close_price
                price_change = last_price - first_price
                price_change_percent = (price_change / first_price) * 100

            # Calculate average sentiment
            avg_sentiment = 0
            if sentiment_data:
                avg_sentiment = sum(s.avg_sentiment for s in sentiment_data) / len(sentiment_data)

            stock_comparison = {
                'symbol': symbol,
                'current_sentiment': latest_sentiment.avg_sentiment if latest_sentiment else 0,
                'average_sentiment': round(avg_sentiment, 3),
                'current_price': latest_price.close_price if latest_price else 0,
                'price_change': round(price_change, 2),
                'price_change_percent': round(price_change_percent, 2),
                'total_posts': sum(s.post_count for s in sentiment_data),
                'prediction': {
                    'direction': current_prediction.predicted_direction if current_prediction else None,
                    'confidence': current_prediction.confidence if current_prediction else None
                },
                'sentiment_history': [
                    {
                        'date': s.date.isoformat(),
                        'sentiment': s.avg_sentiment,
                        'post_count': s.post_count
                    } for s in sentiment_data
                ],
                'price_history': [
                    {
                        'date': p.date.isoformat(),
                        'close_price': p.close_price,
                        'volume': p.volume
                    } for p in price_data
                ]
            }

            comparison_data.append(stock_comparison)

        return jsonify({
            'comparison_data': comparison_data,
            'period': f"{start_date.isoformat()} to {date.today().isoformat()}",
            'days': days
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/compare/metrics/<symbols>', methods=['GET'])
def get_comparison_metrics(symbols):
    """Get quick comparison metrics for stocks"""
    try:
        symbol_list = symbols.upper().split(',')
        if len(symbol_list) < 2:
            return jsonify({'error': 'At least 2 stocks required'}), 400

        metrics = []
        today = date.today()

        for symbol in symbol_list:
            # Latest sentiment
            latest_sentiment = db.session.query(SentimentSummary)\
                .filter_by(symbol=symbol)\
                .order_by(SentimentSummary.date.desc())\
                .first()

            # Latest price
            latest_price = db.session.query(StockPrice)\
                .filter_by(symbol=symbol)\
                .order_by(StockPrice.date.desc())\
                .first()

            # Current prediction
            prediction = db.session.query(Prediction)\
                .filter_by(symbol=symbol, prediction_date=today)\
                .first()

            metrics.append({
                'symbol': symbol,
                'sentiment_score': latest_sentiment.avg_sentiment if latest_sentiment else 0,
                'post_count': latest_sentiment.post_count if latest_sentiment else 0,
                'current_price': latest_price.close_price if latest_price else 0,
                'prediction_direction': prediction.predicted_direction if prediction else None,
                'prediction_confidence': prediction.confidence if prediction else None,
                'last_updated': latest_sentiment.date.isoformat() if latest_sentiment else None
            })

        return jsonify({'metrics': metrics})

    except Exception as e:
        return jsonify({'error': str(e)}), 500