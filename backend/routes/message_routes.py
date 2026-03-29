from flask import Blueprint, request, jsonify
import uuid
from datetime import datetime, timedelta
from database import get_db
from helpers import get_current_user, now

message_bp = Blueprint("messages", __name__)


def _require_trip_member(conn, trip_id, user_id):
    return conn.execute(
        "SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?",
        (trip_id, user_id),
    ).fetchone()


@message_bp.route("/<trip_id>", methods=["GET"])
def get_messages(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "You are not a member of this trip"}), 403

    messages = conn.execute(
        """
        SELECT m.id, m.text, m.sent_at, m.mentions,
               u.id AS user_id, u.name AS user_name, u.profile_picture
        FROM messages m
        JOIN users u ON m.user_id = u.id
                LEFT JOIN message_hidden mh ON mh.message_id = m.id AND mh.user_id = ?
        WHERE m.trip_id = ?
                    AND mh.message_id IS NULL
        ORDER BY m.sent_at ASC
        """,
                (user_id, trip_id),
    ).fetchall()

    result = []
    for msg in messages:
        reactions = conn.execute(
            """
            SELECT emoji, COUNT(*) AS count
            FROM message_reactions
            WHERE message_id = ?
            GROUP BY emoji
            """,
            (msg["id"],),
        ).fetchall()

        read_count = conn.execute(
            "SELECT COUNT(*) AS count FROM read_receipts WHERE message_id = ?",
            (msg["id"],),
        ).fetchone()["count"]

        file_row = conn.execute(
            """
            SELECT file_name, file_data, file_type
            FROM message_files
            WHERE message_id = ?
            ORDER BY uploaded_at DESC
            LIMIT 1
            """,
            (msg["id"],),
        ).fetchone()

        result.append(
            {
                "id": msg["id"],
                "text": msg["text"],
                "time": msg["sent_at"][11:16],
                "userId": msg["user_id"],
                "userName": msg["user_name"],
                "profilePic": msg["profile_picture"],
                "mentions": msg["mentions"].split(",") if msg["mentions"] else [],
                "reactions": [{"emoji": r["emoji"], "count": r["count"]} for r in reactions],
                "readCount": read_count,
                "file": (
                    {
                        "name": file_row["file_name"],
                        "data": file_row["file_data"],
                        "type": file_row["file_type"],
                    }
                    if file_row
                    else None
                ),
            }
        )

    conn.close()
    return jsonify(result), 200


@message_bp.route("/<trip_id>", methods=["POST"])
def send_message(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    mentions = data.get("mentions") or []
    file_data = data.get("file_data")
    file_name = data.get("file_name") or "image"
    file_type = data.get("file_type") or "image/jpeg"

    if not text and not file_data:
        return jsonify({"error": "Message cannot be empty"}), 400

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "You are not a member of this trip"}), 403

    msg_id = str(uuid.uuid4())
    sent_at = now()

    conn.execute(
        """
        INSERT INTO messages (id, trip_id, user_id, text, sent_at, mentions)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (msg_id, trip_id, user_id, text if text else "[Image shared]", sent_at, ",".join(mentions)),
    )

    if file_data:
        file_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO message_files (id, message_id, file_name, file_data, file_type, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (file_id, msg_id, file_name, file_data, file_type, sent_at),
        )

    conn.commit()
    conn.close()

    return jsonify(
        {
            "id": msg_id,
            "text": text if text else "[Image shared]",
            "time": sent_at[11:16],
            "userId": user_id,
            "mentions": mentions,
            "file": ({"name": file_name, "data": file_data, "type": file_type} if file_data else None),
        }
    ), 201


@message_bp.route("/<trip_id>/messages/<message_id>/read", methods=["POST"])
def mark_message_read(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    receipt_id = str(uuid.uuid4())
    read_at = now()

    conn.execute(
        """
        INSERT INTO read_receipts (id, message_id, user_id, read_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (message_id, user_id)
        DO UPDATE SET id = excluded.id, read_at = excluded.read_at
        """,
        (receipt_id, message_id, user_id, read_at),
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/messages/<message_id>/react", methods=["POST"])
def react_to_message(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    emoji = data.get("emoji", "")

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    reaction_id = str(uuid.uuid4())
    reacted_at = now()

    conn.execute(
        """
        INSERT INTO message_reactions (id, message_id, user_id, emoji, reacted_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (message_id, user_id, emoji)
        DO UPDATE SET id = excluded.id, reacted_at = excluded.reacted_at
        """,
        (reaction_id, message_id, user_id, emoji, reacted_at),
    )

    conn.commit()
    conn.close()

    return jsonify({"emoji": emoji, "success": True}), 200


@message_bp.route("/<trip_id>/messages/<message_id>", methods=["DELETE"])
def delete_message(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    data = request.get_json(silent=True) or {}
    mode = (data.get("mode") or "me").strip().lower()

    msg = conn.execute(
        "SELECT id, user_id FROM messages WHERE id = ? AND trip_id = ?",
        (message_id, trip_id),
    ).fetchone()

    if not msg:
        conn.close()
        return jsonify({"error": "Message not found"}), 404

    if mode == "me":
        conn.execute(
            """
            INSERT INTO message_hidden (user_id, message_id, hidden_at)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, message_id)
            DO NOTHING
            """,
            (user_id, message_id, now()),
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Message hidden for you"}), 200

    if mode != "everyone":
        conn.close()
        return jsonify({"error": "Invalid delete mode"}), 400

    if msg["user_id"] != user_id:
        conn.close()
        return jsonify({"error": "Only sender can delete for everyone"}), 403

    conn.execute("DELETE FROM message_hidden WHERE message_id = ?", (message_id,))
    conn.execute("DELETE FROM message_files WHERE message_id = ?", (message_id,))
    conn.execute("DELETE FROM message_reactions WHERE message_id = ?", (message_id,))
    conn.execute("DELETE FROM read_receipts WHERE message_id = ?", (message_id,))
    conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Message deleted for everyone"}), 200


@message_bp.route("/<trip_id>/messages/<message_id>/react", methods=["DELETE"])
def remove_reaction(trip_id, message_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    emoji = data.get("emoji", "")

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    conn.execute(
        """
        DELETE FROM message_reactions
        WHERE message_id = ? AND user_id = ? AND emoji = ?
        """,
        (message_id, user_id, emoji),
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/typing", methods=["POST"])
def set_typing_status(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    conn.execute(
        """
        INSERT INTO typing_status (user_id, trip_id, typing_at)
        VALUES (?, ?, ?)
        ON CONFLICT (user_id, trip_id)
        DO UPDATE SET typing_at = excluded.typing_at
        """,
        (user_id, trip_id, now()),
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True}), 200


@message_bp.route("/<trip_id>/typing", methods=["GET"])
def get_typing_status(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    typing_rows = conn.execute(
        """
        SELECT u.id, u.name, t.typing_at
        FROM typing_status t
        JOIN users u ON t.user_id = u.id
        WHERE t.trip_id = ?
          AND t.user_id != ?
        """,
        (trip_id, user_id),
    ).fetchall()

    conn.close()

    threshold = datetime.utcnow() - timedelta(seconds=3)
    typing = []
    for t in typing_rows:
        try:
            ts = datetime.fromisoformat(t["typing_at"])
        except Exception:
            continue
        if ts > threshold:
            typing.append(t)

    return jsonify([
        {
            "userId": t["id"],
            "userName": t["name"],
        }
        for t in typing
    ]), 200


@message_bp.route("/<trip_id>/upload", methods=["POST"])
def upload_file(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if not _require_trip_member(conn, trip_id, user_id):
        conn.close()
        return jsonify({"error": "Not a member"}), 403

    file_data = request.form.get("file_data")
    file_name = request.form.get("file_name", "image")
    file_type = request.form.get("file_type", "image/jpeg")

    if not file_data:
        conn.close()
        return jsonify({"error": "No file data"}), 400

    msg_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4())
    uploaded_at = now()

    conn.execute(
        """
        INSERT INTO messages (id, trip_id, user_id, text, sent_at, mentions)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (msg_id, trip_id, user_id, "[Image shared]", uploaded_at, ""),
    )

    conn.execute(
        """
        INSERT INTO message_files (id, message_id, file_name, file_data, file_type, uploaded_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (file_id, msg_id, file_name, file_data, file_type, uploaded_at),
    )

    conn.commit()
    conn.close()

    return jsonify({"fileId": file_id, "messageId": msg_id, "fileName": file_name, "fileType": file_type}), 201
