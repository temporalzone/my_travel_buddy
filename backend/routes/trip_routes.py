from flask import Blueprint, request, jsonify
import uuid
from database import get_db
from helpers import get_current_user, now, send_join_request_email

trip_bp = Blueprint("trips", __name__)

@trip_bp.route("/", methods=["GET"])
def get_all_trips():
    current_user = get_current_user()
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

        pending_count = conn.execute(
            "SELECT COUNT(1) AS c FROM join_requests WHERE trip_id = ? AND status = 'pending'",
            (trip["id"],)
        ).fetchone()["c"]

        my_pending = False
        if current_user:
            row = conn.execute(
                "SELECT 1 FROM join_requests WHERE trip_id = ? AND requester_id = ? AND status = 'pending'",
                (trip["id"], current_user)
            ).fetchone()
            my_pending = bool(row)

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
            "createdAt": trip["created_at"],
            "pendingCount": pending_count,
            "myRequestPending": my_pending
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

    if trip["host_id"] == user_id:
        conn.close()
        return jsonify({"error": "You are the creator of this trip"}), 400

    if trip["seats"] <= 0:
        conn.close()
        return jsonify({"error": "This trip is full!"}), 400

    already = conn.execute("""
        SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?
    """, (trip_id, user_id)).fetchone()

    if already:
        conn.close()
        return jsonify({"error": "You already joined this trip"}), 400

    pending = conn.execute(
        "SELECT 1 FROM join_requests WHERE trip_id = ? AND requester_id = ? AND status = 'pending'",
        (trip_id, user_id)
    ).fetchone()

    if pending:
        conn.close()
        return jsonify({"message": "Join request already pending approval."}), 200

    req_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO join_requests (id, trip_id, requester_id, status, requested_at) VALUES (?, ?, ?, 'pending', ?)",
        (req_id, trip_id, user_id, now())
    )

    host = conn.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (trip["host_id"],)
    ).fetchone()
    requester = conn.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    conn.commit()
    conn.close()

    if host and requester:
        sent, msg = send_join_request_email(
            host["email"],
            host["name"],
            trip["title"],
            requester["name"],
            requester["email"]
        )
        if not sent:
            print(f"join-request email failed: {msg}")

    return jsonify({
        "message": "Request sent. You will be added once the creator approves.",
        "request_id": req_id
    }), 200


@trip_bp.route("/requests/pending", methods=["GET"])
def get_pending_requests_for_host():
    host_id = get_current_user()
    if not host_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    rows = conn.execute("""
        SELECT jr.id, jr.trip_id, jr.requested_at,
               t.title AS trip_title,
               u.id AS requester_id, u.name AS requester_name, u.email AS requester_email
        FROM join_requests jr
        JOIN trips t ON jr.trip_id = t.id
        JOIN users u ON jr.requester_id = u.id
        WHERE t.host_id = ? AND jr.status = 'pending'
        ORDER BY jr.requested_at DESC
    """, (host_id,)).fetchall()
    conn.close()

    return jsonify([
        {
            "id": r["id"],
            "tripId": r["trip_id"],
            "tripTitle": r["trip_title"],
            "requesterId": r["requester_id"],
            "requesterName": r["requester_name"],
            "requesterEmail": r["requester_email"],
            "requestedAt": r["requested_at"]
        }
        for r in rows
    ]), 200


@trip_bp.route("/requests/<request_id>/approve", methods=["POST"])
def approve_join_request(request_id):
    host_id = get_current_user()
    if not host_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    row = conn.execute("""
        SELECT jr.id, jr.trip_id, jr.requester_id, jr.status,
               t.host_id, t.seats
        FROM join_requests jr
        JOIN trips t ON jr.trip_id = t.id
        WHERE jr.id = ?
    """, (request_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Request not found"}), 404

    if row["host_id"] != host_id:
        conn.close()
        return jsonify({"error": "Only trip creator can approve"}), 403

    if row["status"] != "pending":
        conn.close()
        return jsonify({"error": "Request already processed"}), 400

    if row["seats"] <= 0:
        conn.close()
        return jsonify({"error": "Trip is full"}), 400

    already = conn.execute(
        "SELECT 1 FROM trip_members WHERE trip_id = ? AND user_id = ?",
        (row["trip_id"], row["requester_id"])
    ).fetchone()

    if not already:
        conn.execute(
            "INSERT INTO trip_members (trip_id, user_id, joined_at) VALUES (?, ?, ?)",
            (row["trip_id"], row["requester_id"], now())
        )
        conn.execute("UPDATE trips SET seats = seats - 1 WHERE id = ?", (row["trip_id"],))

    conn.execute(
        "UPDATE join_requests SET status = 'approved', reviewed_at = ? WHERE id = ?",
        (now(), request_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Request approved. User added to the trip."}), 200


@trip_bp.route("/requests/<request_id>/reject", methods=["POST"])
def reject_join_request(request_id):
    host_id = get_current_user()
    if not host_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    row = conn.execute("""
        SELECT jr.id, jr.status, t.host_id
        FROM join_requests jr
        JOIN trips t ON jr.trip_id = t.id
        WHERE jr.id = ?
    """, (request_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Request not found"}), 404

    if row["host_id"] != host_id:
        conn.close()
        return jsonify({"error": "Only trip creator can reject"}), 403

    if row["status"] != "pending":
        conn.close()
        return jsonify({"error": "Request already processed"}), 400

    conn.execute(
        "UPDATE join_requests SET status = 'rejected', reviewed_at = ? WHERE id = ?",
        (now(), request_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Request rejected."}), 200