from flask import Flask
from flask_cors import CORS
import os
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

# Print registered routes only when debugging is explicitly enabled.
if os.getenv("DEBUG_ROUTES", "false").lower() == "true":
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        if rule.endpoint != "static":
            methods = ",".join(sorted(m for m in rule.methods if m in {"GET", "POST", "PUT", "DELETE", "OPTIONS"}))
            print(f"ROUTE {rule.rule} [{methods}]")

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", "5000"))
    print(f"🌍 Travel Buddy backend running on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)