from flask import Blueprint, request, jsonify
import uuid
from database import get_db
from helpers import get_current_user, now

trip_bp = Blueprint("trips", __name__)

@trip_bp.route("/", methods=["GET"])
def get_all_trips():
    conn = get_db()
    trips = conn.execute(
        "SELECT * FROM trips ORDER BY created_at DESC"
    ).fetchall()

    result = []
    for trip in trips:
        members = conn.execute("""
            SELECT u.id, u.name FROM trip_members tm
            JOIN users u ON tm.user_id = u.id
            WHERE tm.trip_id = ?
        """, (trip["id"],)).fetchall()

        result.append({
            "id":        trip["id"],
            "title":     trip["title"],
            "dest":      trip["destination"],
            "emoji":     trip["emoji"],
            "dates":     trip["dates"],
            "duration":  trip["duration"],
            "budget":    trip["budget"],
            "style":     trip["style"],
            "seats":     trip["seats"],
            "total":     trip["total_seats"],
            "tags":      trip["tags"].split(",") if trip["tags"] else [],
            "hostId":    trip["host_id"],
            "memberIds": [m["id"] for m in members],
            "createdAt": trip["created_at"]
        })

    conn.close()
    return jsonify(result), 200


@trip_bp.route("/", methods=["POST"])
def create_trip():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data.get("title") or not data.get("dest") or not data.get("dates"):
        return jsonify({"error": "Title, destination and dates are required"}), 400

    trip_id = str(uuid.uuid4())
    total   = int(data.get("seats", 4))
    created = now()

    conn = get_db()
    conn.execute("""
        INSERT INTO trips
        (id, title, destination, emoji, dates, duration, budget, style, seats, total_seats, tags, host_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trip_id,
        data["title"].strip(),
        data["dest"].strip(),
        data.get("emoji", "🌍"),
        data["dates"].strip(),
        data.get("duration", "TBD"),
        data.get("budget", "Mid-range"),
        data.get("style", "Adventure"),
        total - 1,
        total,
        ",".join(data.get("tags", [])),
        user_id,
        created
    ))

    conn.execute("""
        INSERT INTO trip_members (trip_id, user_id, joined_at)
        VALUES (?, ?, ?)
    """, (trip_id, user_id, created))

    conn.execute("""
        INSERT INTO messages (id, trip_id, user_id, text, sent_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()), trip_id, user_id,
        f"Hey! Just created this trip to {data['dest'].strip()}. Who's joining? 🎉",
        created
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Trip created!", "trip_id": trip_id}), 201


@trip_bp.route("/<trip_id>/join", methods=["POST"])
def join_trip(trip_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    trip = conn.execute(
        "SELECT * FROM trips WHERE id = ?", (trip_id,)
    ).fetchone()

    if not trip:
        conn.close()
        return jsonify({"error": "Trip not found"}), 404

    if trip["seats"] <= 0:
        conn.close()
        return jsonify({"error": "This trip is full!"}), 400

    already = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if already:
        conn.close()
        return jsonify({"error": "You already joined this trip"}), 400

    conn.execute("""
        INSERT INTO trip_members (trip_id, user_id, joined_at)
        VALUES (?, ?, ?)
    """, (trip_id, user_id, now()))

    conn.execute(
        "UPDATE trips SET seats = seats - 1 WHERE id = ?", (trip_id,)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "You joined the trip! 🎉"}), 200