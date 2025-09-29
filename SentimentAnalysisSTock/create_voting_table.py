#!/usr/bin/env python3
"""
Create the PredictionVote table for the voting system
"""

import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app
from backend.models.models import db, PredictionVote

def create_voting_table():
    """Create the PredictionVote table"""
    print("Creating PredictionVote table...")

    app, _ = create_app()

    with app.app_context():
        try:
            # Create the table
            db.create_all()
            print("✅ PredictionVote table created successfully!")

            # Verify table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()

            if 'prediction_votes' in tables:
                print("✅ Table 'prediction_votes' confirmed in database")

                # Show table structure
                columns = inspector.get_columns('prediction_votes')
                print("\n📋 Table structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("❌ Table creation may have failed")

        except Exception as e:
            print(f"❌ Error creating table: {e}")
            raise

if __name__ == "__main__":
    create_voting_table()