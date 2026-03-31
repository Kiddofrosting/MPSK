"""
db.py — single source of truth for the MongoDB connection.

Uses plain pymongo (not Flask-PyMongo) so the connection is
established immediately and fails loudly if MONGO_URI is wrong.
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None


def init_db(app):
    global _client, _db

    uri = app.config.get('MONGO_URI') or os.getenv('MONGO_URI', '')
    if not uri or 'localhost' in uri:
        # Warn loudly — localhost will never work on Render
        print("⚠️  WARNING: MONGO_URI points to localhost or is not set.")
        print("   Set MONGO_URI to your MongoDB Atlas connection string.")

    try:
        _client = MongoClient(uri, serverSelectionTimeoutMS=10000)
        # Extract database name from URI, default to mpsk_db
        db_name = uri.split('/')[-1].split('?')[0] or 'mpsk_db'
        _db = _client[db_name]
        # Verify connection
        _client.admin.command('ping')
        print(f"✅ MongoDB connected — database: '{db_name}'")
    except (ConnectionFailure, ConfigurationError, Exception) as e:
        print(f"❌ MongoDB connection FAILED: {e}")
        print("   Check your MONGO_URI in .env or Render environment variables.")
        _db = None

    app.db = _db


def get_db():
    return _db
