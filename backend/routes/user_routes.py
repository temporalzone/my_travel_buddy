from flask import Blueprint, request, jsonify
import bcrypt
from database import get_db
from helpers import get_current_user

user_bp = Blueprint("users", __name__)

@user_bp.route("/me", methods=["GET"])
def get_me():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id":        user["id"],
        "name":      user["name"],
        "email":     user["email"],
        "location":  user["location"],
        "bio":       user["bio"],
        "interests": user["interests"].split(",") if user["interests"] else [],
        "joined_at": user["joined_at"],
        "age":       user["age"],
        "gender":    user["gender"],
        "profile_picture": user["profile_picture"]
    }), 200


@user_bp.route("/me", methods=["PUT"])
def update_profile():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    conn = get_db()
    conn.execute("""
        UPDATE users
        SET name = ?, email = ?, location = ?, bio = ?, interests = ?, age = ?, gender = ?, profile_picture = ?
        WHERE id = ?
    """, (
        data["name"].strip(),
        data["email"].lower().strip(),
        data.get("location", ""),
        data.get("bio", ""),
        ",".join(data.get("interests", [])),
        data.get("age"),
        data.get("gender"),
        data.get("profile_picture"),
        user_id
    ))
    conn.commit()
    conn.close()

    return jsonify({"message": "Profile updated!"}), 200


@user_bp.route("/me/password", methods=["PUT"])
def change_password():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("old_password") or not data.get("new_password"):
        return jsonify({"error": "Both passwords are required"}), 400

    if len(data["new_password"]) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()

    if not bcrypt.checkpw(
        data["old_password"].encode("utf-8"),
        user["password"].encode("utf-8")
    ):
        conn.close()
        return jsonify({"error": "Current password is incorrect"}), 400

    new_hash = bcrypt.hashpw(
        data["new_password"].encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn.execute(
        "UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Password changed successfully!"}), 200


@user_bp.route("/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id":        user["id"],
        "name":      user["name"],
        "location":  user["location"],
        "bio":       user["bio"],
        "interests": user["interests"].split(",") if user["interests"] else [],
        "age":       user["age"],
        "gender":    user["gender"],
        "profile_picture": user["profile_picture"]
    }), 200