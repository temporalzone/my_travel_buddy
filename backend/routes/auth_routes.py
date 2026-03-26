from flask import Blueprint, request, jsonify
import bcrypt
import uuid
import os
import json
import random
from datetime import datetime, timedelta
from database import get_db
from helpers import create_token, now, send_reset_email, create_reset_token, verify_reset_token, FRONTEND_URL, send_registration_otp_email

auth_bp = Blueprint("auth", __name__)
ALLOW_RESET_LINK_FALLBACK = os.getenv("ALLOW_RESET_LINK_FALLBACK", "false").lower() == "true"


def _build_user_response(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "location": user["location"],
        "bio": user["bio"],
        "interests": user["interests"].split(",") if user["interests"] else [],
        "joined_at": user["joined_at"],
        "age": user["age"],
        "gender": user["gender"],
        "profile_picture": user["profile_picture"]
    }

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Name, email and password are required"}), 400

    if "@" not in data["email"]:
        return jsonify({"error": "Enter a valid email address"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db()

    existing = conn.execute(
        "SELECT id FROM users WHERE email = ?",
        (data["email"].lower().strip(),)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    hashed = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user_id = str(uuid.uuid4())
    joined  = now()

    conn.execute("""
        INSERT INTO users (id, name, email, password, location, bio, interests, joined_at, age, gender, profile_picture)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        data["name"].strip(),
        data["email"].lower().strip(),
        hashed,
        data.get("location", "Earth 🌍"),
        data.get("bio", "New traveler!"),
        "",
        joined,
        data.get("age"),
        data.get("gender"),
        data.get("profile_picture")
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "token": create_token(user_id),
        "user": {
            "id": user_id,
            "name": data["name"].strip(),
            "email": data["email"].lower().strip(),
            "location": data.get("location", "Earth 🌍"),
            "bio": data.get("bio", "New traveler!"),
            "interests": [],
            "joined_at": joined,
            "age": data.get("age"),
            "gender": data.get("gender"),
            "profile_picture": data.get("profile_picture")
        }
    }), 201


@auth_bp.route("/request-register-otp", methods=["POST"])
def request_register_otp():
    data = request.get_json()

    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Name, email and password are required"}), 400

    email = data["email"].lower().strip()
    if "@" not in email:
        return jsonify({"error": "Enter a valid email address"}), 400

    if len(data["password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    otp_code = str(random.randint(100000, 999999))
    otp_id = str(uuid.uuid4())
    payload = json.dumps({
        "name": data.get("name", "").strip(),
        "email": email,
        "password": data.get("password"),
        "location": data.get("location", "Earth 🌍"),
        "bio": data.get("bio", "New traveler!"),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "profile_picture": data.get("profile_picture")
    })
    expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

    conn.execute("DELETE FROM email_otps WHERE email = ?", (email,))
    conn.execute(
        "INSERT INTO email_otps (id, email, otp_code, payload, expires_at, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (otp_id, email, otp_code, payload, expires_at, now())
    )
    conn.commit()
    conn.close()

    sent, msg = send_registration_otp_email(email, otp_code)
    if not sent:
        return jsonify({"error": "Could not send OTP email. Try again later."}), 500

    return jsonify({"message": "OTP sent to your email."}), 200


@auth_bp.route("/verify-register-otp", methods=["POST"])
def verify_register_otp():
    data = request.get_json()
    email = (data.get("email") or "").lower().strip()
    otp = (data.get("otp") or "").strip()

    if not email or not otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    conn = get_db()
    row = conn.execute(
        "SELECT * FROM email_otps WHERE email = ? ORDER BY created_at DESC LIMIT 1",
        (email,)
    ).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "OTP not found. Please request a new one."}), 404

    if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
        conn.execute("DELETE FROM email_otps WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"error": "OTP expired. Please request a new one."}), 400

    if row["otp_code"] != otp:
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 400

    payload = json.loads(row["payload"])
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing:
        conn.execute("DELETE FROM email_otps WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    user_id = str(uuid.uuid4())
    joined = now()
    hashed = bcrypt.hashpw(payload["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn.execute("""
        INSERT INTO users (id, name, email, password, location, bio, interests, joined_at, age, gender, profile_picture)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        payload["name"],
        payload["email"],
        hashed,
        payload.get("location", "Earth 🌍"),
        payload.get("bio", "New traveler!"),
        "",
        joined,
        payload.get("age"),
        payload.get("gender"),
        payload.get("profile_picture")
    ))

    conn.execute("DELETE FROM email_otps WHERE email = ?", (email,))
    conn.commit()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    return jsonify({
        "token": create_token(user_id),
        "user": _build_user_response(user)
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (data["email"].lower().strip(),)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Incorrect email or password"}), 401

    pw_ok = bcrypt.checkpw(
        data["password"].encode("utf-8"),
        user["password"].encode("utf-8")
    )

    if not pw_ok:
        return jsonify({"error": "Incorrect email or password"}), 401

    return jsonify({
        "token": create_token(user["id"]),
        "user": _build_user_response(user)
    }), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    if not data.get("email"):
        return jsonify({"error": "Email is required"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (data["email"].lower().strip(),)
    ).fetchone()
    conn.close()

    if not user:
        # Do not reveal whether an account exists for this email.
        return jsonify({"message": "If that email exists, a reset link has been sent."}), 200

    reset_token = create_reset_token(data["email"].lower().strip())
    sent, send_message = send_reset_email(data["email"].lower().strip(), reset_token)

    if not sent:
        print(f"forgot-password send failure: {send_message}")

        if ALLOW_RESET_LINK_FALLBACK:
            # Optional fallback for controlled debugging only.
            base_url = (FRONTEND_URL or "").rstrip("/")
            if base_url.endswith("/my_travel_buddy"):
                reset_link = f"{base_url}/?reset_token={reset_token}"
            else:
                reset_link = f"{base_url}/my_travel_buddy/?reset_token={reset_token}"

            return jsonify({
                "message": "Email delivery failed, but you can still reset using this link.",
                "reset_link": reset_link
            }), 200

        return jsonify({"error": "Could not send email. Try again later."}), 500

    return jsonify({"message": "If that email exists, a reset link has been sent."}), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """
    POST /api/auth/reset-password
    Body: { token, new_password }
    """
    data = request.get_json()

    if not data.get("token") or not data.get("new_password"):
        return jsonify({"error": "Token and new password are required"}), 400

    if len(data["new_password"]) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    # Token verify karo
    email = verify_reset_token(data["token"])
    if not email:
        return jsonify({"error": "Invalid or expired reset link"}), 400

    # Naya password hash karo
    new_hash = bcrypt.hashpw(
        data["new_password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = get_db()
    conn.execute(
        "UPDATE users SET password = ? WHERE email = ?",
        (new_hash, email)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Password reset successfully!"}), 200