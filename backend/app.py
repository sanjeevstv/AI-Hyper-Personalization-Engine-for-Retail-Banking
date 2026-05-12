from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    from routes.customers import customers_bp
    from routes.ingestion import ingestion_bp
    from routes.recommendations import recommendations_bp
    from routes.messaging import messaging_bp

    app.register_blueprint(customers_bp, url_prefix="/api/customers")
    app.register_blueprint(ingestion_bp, url_prefix="/api/ingest")
    app.register_blueprint(recommendations_bp, url_prefix="/api")
    app.register_blueprint(messaging_bp, url_prefix="/api")

    with app.app_context():
        import models.models  # noqa: F401 — register models for create_all
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
