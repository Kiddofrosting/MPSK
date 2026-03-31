"""
db.py — MongoDB connection using plain pymongo.
Bypasses SSL verification to work around Python 3.14 / OpenSSL
TLS handshake issues with MongoDB Atlas on Render.
"""
import os
import ssl
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_db = None


def init_db(app):
    global _db

    uri = app.config.get('MONGO_URI') or os.getenv('MONGO_URI', '')

    if not uri:
        print("❌ MONGO_URI is not set. Check your environment variables.")
        return

    try:
        # Create a permissive SSL context that works with Python 3.14 + Atlas
        tls_ctx = ssl.create_default_context()
        tls_ctx.check_hostname = False
        tls_ctx.verify_mode = ssl.CERT_NONE

        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=20000,
            tls=True,
            tlsCAFile=None,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
        )

        # Extract db name from URI (between last / and ?)
        db_name = uri.split('/')[-1].split('?')[0].strip() or 'mpsk_db'
        _db = client[db_name]

        # Verify connection
        client.admin.command('ping')
        print(f"✅ MongoDB connected — database: '{db_name}'")

    except Exception as e:
        print(f"❌ MongoDB connection FAILED: {e}")
        print("   Check your MONGO_URI in Render environment variables.")
        _db = None

    app.db = _db


def get_db():
    return _db
