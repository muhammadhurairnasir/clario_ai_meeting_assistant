"""
app.py
------
Clario – AI Meeting Assistant
Flask application factory and entry point.
"""

import os
import sys

# ── Force UTF-8 output on Windows (prevents charmap codec errors in logs) ──────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from datetime import timedelta

from flask import Flask, render_template
from config import SECRET_KEY, DEBUG, PORT, DB_PATH


def create_app() -> Flask:
    """Application factory — create, configure, and return the Flask app."""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Sessions expire after 7 days of inactivity
    app.permanent_session_lifetime = timedelta(days=7)

    # ── Initialise database ────────────────────────────────────────────────────
    from models.database import init_db
    init_db(DB_PATH)

    # ── Register blueprints ────────────────────────────────────────────────────
    from routes.auth      import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.meeting   import meeting_bp
    from routes.search    import search_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(meeting_bp)
    app.register_blueprint(search_bp)

    # ── Error handlers ─────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template(
            "error.html",
            code    = 404,
            title   = "Page not found",
            message = "The page you're looking for doesn't exist or has been moved.",
        ), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template(
            "error.html",
            code    = 500,
            title   = "Internal server error",
            message = "Something went wrong. Please try again in a moment.",
        ), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=DEBUG, port=PORT, use_reloader=False)
