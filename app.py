from flask import Flask, request, jsonify
from extensions import db
import config
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from threading import Thread

# import fungsi summary kamu (misal ollama)
from ollama_summarize import summarize_text  # pastikan file ini ada


def create_app():
    app = Flask(__name__)

    # Konfigurasi database
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

    # Konfigurasi JWT
    app.config["JWT_SECRET_KEY"] = "super-secret"

    # Init extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/*": {
        "origins": "http://localhost:5173",
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # Import & register blueprint
    from routes.meeting_rooms import rooms_bp
    from routes.meetings import meetings_bp
    from routes.employees import employees_bp
    from routes.status import status_bp
    from routes.users import users_bp
    from routes.attendance import attendance_bp
    from routes.summarization import summarization_bp



    app.register_blueprint(rooms_bp, url_prefix="/meeting_rooms")
    app.register_blueprint(meetings_bp, url_prefix="/meetings")
    app.register_blueprint(employees_bp, url_prefix="/employees")
    app.register_blueprint(status_bp, url_prefix="/status")
    app.register_blueprint(users_bp, url_prefix="/auth")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(summarization_bp, url_prefix="/summarization")



    # Buat tabel kalau belum ada
    with app.app_context():
        db.create_all()

    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
