from flask import Blueprint, request, jsonify
import uuid
from database import get_db
from helpers import get_current_user, now

message_bp = Blueprint("messages", __name__)

@message_bp.route("/<trip_id>", methods=["GET"])
def get_messages(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()

    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "You are not a member of this trip"}), 403

    messages = conn.execute("""
        SELECT m.id, m.text, m.sent_at, u.id as user_id, u.name as user_name
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.trip_id = ?
        ORDER BY m.sent_at ASC
    """, (trip_id,)).fetchall()

    conn.close()

    return jsonify([{
        "id":       msg["id"],
        "text":     msg["text"],
        "time":     msg["sent_at"][11:16],
        "userId":   msg["user_id"],
        "userName": msg["user_name"]
    } for msg in messages]), 200


@message_bp.route("/<trip_id>", methods=["POST"])
def send_message(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("text") or not data["text"].strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    conn = get_db()

    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "You are not a member of this trip"}), 403

    msg_id  = str(uuid.uuid4())
    sent_at = now()

    conn.execute("""
        INSERT INTO messages (id, trip_id, user_id, text, sent_at)
        VALUES (?, ?, ?, ?, ?)
    """, (msg_id, trip_id, user_id, data["text"].strip(), sent_at))

    conn.commit()
    conn.close()

    return jsonify({
        "id":     msg_id,
        "text":   data["text"].strip(),
        "time":   sent_at[11:16],
        "userId": user_id
    }), 201