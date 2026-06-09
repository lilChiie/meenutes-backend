from dotenv import load_dotenv
from google import genai
import os
from flask import Flask
from extensions import db
import config
from flask_cors import CORS
from flask_jwt_extended import JWTManager

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def create_app():
    app = Flask(__name__)

    # Konfigurasi database
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
        config.SQLALCHEMY_TRACK_MODIFICATIONS
    )

    # Konfigurasi JWT
    app.config["JWT_SECRET_KEY"] = "super-secret"

    # Init extensions
    db.init_app(app)
    JWTManager(app)

    CORS(
     app,
    resources={
         r"/*": {
            "origins": "http://localhost:5173",
            "allow_headers": ["Content-Type", "Authorization"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "supports_credentials": True,
        }
    },
)

    # Import & register blueprint
    from routes.users import users_bp
    from routes.events import events_bp
    from routes.event_divisions import event_divisions_bp
    from routes.internal_divisions import internal_divisions_bp
    from routes.meeting_minutes import meeting_minutes_bp
    from routes.summarization import summarization_bp
    from routes.dashboard import dashboard_bp
    from routes.transcription import transcription_bp



    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(events_bp, url_prefix="/events")
    app.register_blueprint(
        event_divisions_bp,
        url_prefix="/event-divisions",
    )
    app.register_blueprint(
        internal_divisions_bp,
        url_prefix="/internal-divisions",
    )
    app.register_blueprint(
        meeting_minutes_bp,
        url_prefix="/meeting-minutes",
    )
    app.register_blueprint(
        summarization_bp,
        url_prefix="/summarization",
    )
    app.register_blueprint(
    dashboard_bp,
    url_prefix="/dashboard"
    )
    app.register_blueprint(transcription_bp, url_prefix="/transcription")
    

    # Buat tabel kalau belum ada
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)