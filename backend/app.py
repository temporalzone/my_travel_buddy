from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth_routes import auth_bp
from routes.trip_routes import trip_bp
from routes.user_routes import user_bp
from routes.message_routes import message_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp,    url_prefix="/api/auth")
app.register_blueprint(trip_bp,    url_prefix="/api/trips")
app.register_blueprint(user_bp,    url_prefix="/api/users")
app.register_blueprint(message_bp, url_prefix="/api/messages")

if __name__ == "__main__":
    init_db()
    print("🌍 Travel Buddy backend running at http://localhost:5000")
    app.run(debug=True, port=5000)