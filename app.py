import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'mpsk-dev-key-2026')
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', '')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB upload limit

    # ── Database ───────────────────────────────────────────────────────────
    from db import init_db
    init_db(app)

    # ── Auth ───────────────────────────────────────────────────────────────
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # ── Custom Jinja2 filters ──────────────────────────────────────────────
    @app.template_filter('money')
    def money_filter(value):
        if value is None or value == '' or value == '—':
            return '—'
        try:
            num = float(str(value).replace(',', ''))
            return f"{num:,.0f}"
        except (ValueError, TypeError):
            return str(value)

    # ── Inject settings into every template ───────────────────────────────
    @app.context_processor
    def inject_globals():
        try:
            from db import get_db
            db = get_db()
            raw = db.settings.find_one({'key': 'site'}) or {} if db else {}
            settings = {k: v for k, v in raw.items() if k != '_id'}
        except Exception:
            settings = {}
        return dict(settings=settings)

    # ── Blueprints ─────────────────────────────────────────────────────────
    from routes.public import public_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ── Seed database on first run ─────────────────────────────────────────
    try:
        from db import get_db
        from utils.db_seed import seed_database
        db = get_db()
        if db is not None:
            seed_database(db)
        else:
            print("⚠️  Skipping seed — no database connection.")
    except Exception as e:
        print(f"⚠️  Seed error: {e}")

    # ── Error handlers ─────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('public/404.html'), 404

    @app.errorhandler(503)
    def service_unavailable(e):
        from flask import render_template
        return render_template('public/503.html'), 503

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
