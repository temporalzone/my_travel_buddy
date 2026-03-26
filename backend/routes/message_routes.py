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
        SELECT m.id, m.text, m.sent_at, m.mentions, u.id as user_id, u.name as user_name, u.profile_picture
        FROM messages m
        JOIN users u ON m.user_id = u.id
        WHERE m.trip_id = ?
        ORDER BY m.sent_at ASC
    """, (trip_id,)).fetchall()

    conn.close()

    result = []
    for msg in messages:
        # Get reactions for this message
        reactions_db = conn = get_db()
        reactions = reactions_db.execute("""
            SELECT emoji, COUNT(*) as count FROM message_reactions 
            WHERE message_id = ? GROUP BY emoji
        """, (msg["id"],)).fetchall()
        reactions_list = [{"emoji": r["emoji"], "count": r["count"]} for r in reactions]
        
        # Get read receipts for this message
        read_count = reactions_db.execute("""
            SELECT COUNT(*) as count FROM read_receipts WHERE message_id = ?
        """, (msg["id"],)).fetchone()["count"]
        reactions_db.close()
        
        result.append({
            "id":           msg["id"],
            "text":         msg["text"],
            "time":         msg["sent_at"][11:16],
            "userId":       msg["user_id"],
            "userName":     msg["user_name"],
            "profilePic":   msg["profile_picture"],
            "mentions":     msg["mentions"].split(",") if msg["mentions"] else [],
            "reactions":    reactions_list,
            "readCount":    read_count
        })

    return jsonify(result), 200


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


@message_bp.route("/<trip_id>/messages/<message_id>/read", methods=["POST"])
def mark_message_read(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    receipt_id = str(uuid.uuid4())
    read_at = now()

    # Upsert read receipt
    conn.execute("""
        INSERT OR REPLACE INTO read_receipts (id, message_id, user_id, read_at)
        VALUES (?, ?, ?, ?)
    """, (receipt_id, message_id, user_id, read_at))

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/messages/<message_id>/react", methods=["POST"])
def react_to_message(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    emoji = data.get("emoji", "👍")

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    reaction_id = str(uuid.uuid4())
    reacted_at = now()

    conn.execute("""
        INSERT OR REPLACE INTO message_reactions (id, message_id, user_id, emoji, reacted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (reaction_id, message_id, user_id, emoji, reacted_at))

    conn.commit()
    conn.close()

    return jsonify({"emoji": emoji, "success": True}), 200


@message_bp.route("/<trip_id>/messages/<message_id>/react", methods=["DELETE"])
def remove_reaction(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    emoji = data.get("emoji", "👍")

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    conn.execute("""
        DELETE FROM message_reactions 
        WHERE message_id = ? AND user_id = ? AND emoji = ?
    """, (message_id, user_id, emoji))

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/typing", methods=["POST"])
def set_typing_status(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    typing_at = now()

    conn.execute("""
        INSERT OR REPLACE INTO typing_status (user_id, trip_id, typing_at)
        VALUES (?, ?, ?)
    """, (user_id, trip_id, typing_at))

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/typing", methods=["GET"])
def get_typing_status(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    typing = conn.execute("""
        SELECT u.id, u.name FROM typing_status t
        JOIN users u ON t.user_id = u.id
        WHERE t.trip_id = ? AND t.user_id != ?
        AND datetime(t.typing_at) > datetime('now', '-3 seconds')
    """, (trip_id, user_id)).fetchall()

    conn.close()

    return jsonify([{
        "userId": t["id"],
        "userName": t["name"]
    } for t in typing]), 200


@message_bp.route("/<trip_id>/upload", methods=["POST"])
def upload_file(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    member = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if not member:
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    file_data = request.form.get("file_data")
    file_name = request.form.get("file_name", "image")
    file_type = request.form.get("file_type", "image/jpeg")

    if not file_data:
        return jsonify({"error": "No file data"}), 400

    file_id = str(uuid.uuid4())
    uploaded_at = now()

    conn.execute("""
        INSERT INTO message_files (id, message_id, file_name, file_data, file_type, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (file_id, file_id, file_name, file_data, file_type, uploaded_at))

    conn.commit()
    conn.close()

    return jsonify({
        "fileId": file_id,
        "fileName": file_name,
        "fileType": file_type
    }), 201