import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from backend.config.config import Config
from backend.models.models import db
from backend.routes.api import api

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS)
    socketio = SocketIO(app, cors_allowed_origins=Config.CORS_ORIGINS)

    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        """Serve the main dashboard"""
        return render_template('index.html')

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('subscribe_updates')
    def handle_subscribe(data):
        """Handle client subscription to real-time updates"""
        print(f"Client subscribed to updates: {data}")

    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)