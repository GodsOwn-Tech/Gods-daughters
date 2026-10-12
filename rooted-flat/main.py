"""
main.py — the Flask app and all API routes.
Run this file to start the server: python main.py
"""
import os
import uuid
import secrets
import sqlite3
import requests
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from database import get_connection, init_db
from auth import hash_password, check_password, make_token, require_auth, optional_auth
from emailer import send_email

load_dotenv()
init_db()  # creates database.db and its tables if they don't exist yet

# static_folder="." + static_url_path="" means Flask serves the HTML/CSS/JS
# files sitting right next to this file — one server for everything, no
# separate frontend server needed.
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)  # harmless to keep even though frontend + backend now share an origin


@app.get("/")
def serve_index():
    return send_from_directory(".", "index.html")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    return uuid.uuid4().hex[:16]


def notify(conn, user_id, ntype, message):
    """Creates a notification for user_id. Call this any time something
    happens that the user should be told about (a reaction, a friend
    request, a prayer on their post, etc). Doesn't commit — caller's
    conn.commit() covers it."""
    conn.execute(
        "INSERT INTO notifications (id, user_id, type, message, read, created_at) VALUES (?, ?, ?, ?, 0, ?)",
        (new_id(), user_id, ntype, message, now_iso()),
    )


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.post("/api/auth/signup")
def signup():
    body = request.get_json(force=True) or {}
    email = (body.get("email") or "").strip()
    password = body.get("password") or ""
    handle = (body.get("handle") or "").strip()

    if not email or not password or not handle:
        return jsonify({"error": "Email, password, and a display name are all required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password should be at least 8 characters."}), 400

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "An account with that email already exists."}), 409

    c.execute("SELECT id FROM users WHERE LOWER(handle) = LOWER(?)", (handle,))
    if c.fetchone():
        conn.close()
        return jsonify({"error": "That display name is taken. Try another."}), 409

    user_id = new_id()
    c.execute(
        "INSERT INTO users (id, email, password_hash, handle, created_at, restricted) VALUES (?, ?, ?, ?, ?, 0)",
        (user_id, email, hash_password(password), handle, now_iso()),
    )
    conn.commit()
    conn.close()

    token = make_token(user_id, handle)
    return jsonify({"token": token, "handle": handle}), 201


@app.post("/api/auth/login")
def login():
    body = request.get_json(force=True) or {}
    # Accepts either email or display name in the same field.
    identifier = (body.get("identifier") or body.get("email") or "").strip()
    password = body.get("password") or ""

    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR LOWER(handle) = LOWER(?)",
        (identifier, identifier),
    )
    user = c.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Incorrect email/username or password."}), 401
    if user["restricted"]:
        return jsonify({"error": "This account has been restricted."}), 403
    if not check_password(password, user["password_hash"]):
        return jsonify({"error": "Incorrect email/username or password."}), 401

    token = make_token(user["id"], user["handle"])
    return jsonify({"token": token, "handle": user["handle"]})


@app.post("/api/auth/forgot-password")
def forgot_password():
    body = request.get_json(force=True) or {}
    email = (body.get("email") or "").strip()
    if not email:
        return jsonify({"error": "Enter the email on your account."}), 400

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()

    # Always return the same message whether or not the email exists —
    # this avoids letting someone check which emails have accounts here.
    if user:
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
        conn.execute(
            "INSERT INTO password_resets (id, user_id, code, expires_at, used, created_at) VALUES (?, ?, ?, ?, 0, ?)",
            (new_id(), user["id"], code, expires_at, now_iso()),
        )
        conn.commit()
        send_email(
            user["email"],
            "Your Rooted password reset code",
            f"Hi {user['handle']},\n\n"
            f"Your password reset code is: {code}\n\n"
            f"This code expires in 15 minutes. If you didn't request this, "
            f"you can safely ignore this email.\n\n— Rooted",
        )
    conn.close()
    return jsonify({"message": "If that email has an account, a reset code has been sent."})


@app.post("/api/auth/reset-password")
def reset_password():
    body = request.get_json(force=True) or {}
    email = (body.get("email") or "").strip()
    code = (body.get("code") or "").strip()
    new_password = body.get("new_password") or ""

    if len(new_password) < 8:
        return jsonify({"error": "New password should be at least 8 characters."}), 400

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"error": "That code isn't valid. Double check the email and code."}), 400

    reset_row = conn.execute(
        "SELECT * FROM password_resets WHERE user_id = ? AND code = ? AND used = 0 ORDER BY created_at DESC LIMIT 1",
        (user["id"], code),
    ).fetchone()

    if not reset_row:
        conn.close()
        return jsonify({"error": "That code isn't valid. Double check the email and code."}), 400

    if datetime.fromisoformat(reset_row["expires_at"]) < datetime.now(timezone.utc):
        conn.close()
        return jsonify({"error": "That code has expired. Request a new one."}), 400

    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(new_password), user["id"]))
    conn.execute("UPDATE password_resets SET used = 1 WHERE id = ?", (reset_row["id"],))
    conn.commit()
    conn.close()
    return jsonify({"message": "Password reset. You can sign in with your new password now."})


# ---------------------------------------------------------------------------
# Account settings — view profile, change handle, change password
# ---------------------------------------------------------------------------

@app.get("/api/account")
@require_auth
def get_account():
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (request.user["id"],)).fetchone()
    conn.close()
    if not user:
        return jsonify({"error": "Account not found."}), 404
    return jsonify({
        "handle": user["handle"],
        "email": user["email"],
        "created_at": user["created_at"],
    })


@app.patch("/api/account/handle")
@require_auth
def update_handle():
    body = request.get_json(force=True) or {}
    new_handle = (body.get("handle") or "").strip()

    if not new_handle:
        return jsonify({"error": "Pick a display name first."}), 400
    if len(new_handle) < 2:
        return jsonify({"error": "Display name should be at least 2 characters."}), 400

    conn = get_connection()
    taken = conn.execute(
        "SELECT id FROM users WHERE LOWER(handle) = LOWER(?) AND id != ?",
        (new_handle, request.user["id"]),
    ).fetchone()
    if taken:
        conn.close()
        return jsonify({"error": "That display name is taken. Try another."}), 409

    conn.execute("UPDATE users SET handle = ? WHERE id = ?", (new_handle, request.user["id"]))
    # Keep past posts consistent with the new name.
    conn.execute("UPDATE prayer_wall SET handle = ? WHERE user_id = ?", (new_handle, request.user["id"]))
    conn.execute("UPDATE gist SET handle = ? WHERE user_id = ?", (new_handle, request.user["id"]))
    conn.commit()
    conn.close()

    # Issue a fresh token since the old one has the outdated handle baked in.
    token = make_token(request.user["id"], new_handle)
    return jsonify({"handle": new_handle, "token": token})


@app.patch("/api/account/password")
@require_auth
def update_password():
    body = request.get_json(force=True) or {}
    current_password = body.get("current_password") or ""
    new_password = body.get("new_password") or ""

    if len(new_password) < 8:
        return jsonify({"error": "New password should be at least 8 characters."}), 400

    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (request.user["id"],)).fetchone()

    if not user or not check_password(current_password, user["password_hash"]):
        conn.close()
        return jsonify({"error": "Current password is incorrect."}), 401

    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(new_password), request.user["id"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Password updated."})


# ---------------------------------------------------------------------------
# Friends
# ---------------------------------------------------------------------------

def get_accepted_friend_handles(conn, user_id):
    """Returns a lowercase set of handles this user is friends with —
    used to make sure people can only tag actual friends or add them to
    a study group."""
    rows = conn.execute(
        """SELECT f.requester_id, f.addressee_id,
                  u1.handle AS requester_handle, u2.handle AS addressee_handle
           FROM friends f
           JOIN users u1 ON u1.id = f.requester_id
           JOIN users u2 ON u2.id = f.addressee_id
           WHERE (f.requester_id = ? OR f.addressee_id = ?) AND f.status = 'accepted'""",
        (user_id, user_id),
    ).fetchall()
    handles = set()
    for r in rows:
        other = r["addressee_handle"] if r["requester_id"] == user_id else r["requester_handle"]
        handles.add(other.lower())
    return handles


@app.post("/api/friends/request")
@require_auth
def send_friend_request():
    body = request.get_json(force=True) or {}
    handle = (body.get("handle") or "").strip()
    if not handle:
        return jsonify({"error": "Enter a display name to add."}), 400

    conn = get_connection()
    target = conn.execute("SELECT * FROM users WHERE LOWER(handle) = LOWER(?)", (handle,)).fetchone()
    if not target:
        conn.close()
        return jsonify({"error": "No one with that display name was found."}), 404
    if target["id"] == request.user["id"]:
        conn.close()
        return jsonify({"error": "You can't add yourself as a friend."}), 400

    existing = conn.execute(
        "SELECT * FROM friends WHERE (requester_id = ? AND addressee_id = ?) OR (requester_id = ? AND addressee_id = ?)",
        (request.user["id"], target["id"], target["id"], request.user["id"]),
    ).fetchone()
    if existing:
        conn.close()
        if existing["status"] == "accepted":
            return jsonify({"error": f"You're already friends with {handle}."}), 409
        return jsonify({"error": "A friend request is already pending between you two."}), 409

    conn.execute(
        "INSERT INTO friends (id, requester_id, addressee_id, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (new_id(), request.user["id"], target["id"], now_iso()),
    )
    notify(conn, target["id"], "friend_request", f"{request.user['handle']} sent you a friend request.")
    conn.commit()
    conn.close()
    return jsonify({"message": f"Friend request sent to {handle}."}), 201


@app.get("/api/friends")
@require_auth
def list_friends():
    conn = get_connection()
    rows = conn.execute(
        """SELECT f.requester_id, f.addressee_id,
                  u1.handle AS requester_handle, u2.handle AS addressee_handle
           FROM friends f
           JOIN users u1 ON u1.id = f.requester_id
           JOIN users u2 ON u2.id = f.addressee_id
           WHERE (f.requester_id = ? OR f.addressee_id = ?) AND f.status = 'accepted'""",
        (request.user["id"], request.user["id"]),
    ).fetchall()
    conn.close()

    friends = []
    for r in rows:
        is_me_requester = r["requester_id"] == request.user["id"]
        friends.append({
            "user_id": r["addressee_id"] if is_me_requester else r["requester_id"],
            "handle": r["addressee_handle"] if is_me_requester else r["requester_handle"],
        })
    return jsonify(friends)


@app.get("/api/friends/requests")
@require_auth
def list_friend_requests():
    conn = get_connection()
    rows = conn.execute(
        """SELECT f.id, u.handle AS requester_handle
           FROM friends f
           JOIN users u ON u.id = f.requester_id
           WHERE f.addressee_id = ? AND f.status = 'pending'""",
        (request.user["id"],),
    ).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "handle": r["requester_handle"]} for r in rows])


@app.post("/api/friends/<request_id>/accept")
@require_auth
def accept_friend_request(request_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM friends WHERE id = ? AND addressee_id = ?", (request_id, request.user["id"])
    ).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "That friend request no longer exists."}), 404
    conn.execute("UPDATE friends SET status = 'accepted' WHERE id = ?", (request_id,))
    notify(conn, row["requester_id"], "friend_accept", f"{request.user['handle']} accepted your friend request.")
    conn.commit()
    conn.close()
    return jsonify({"message": "Friend request accepted."})


@app.post("/api/friends/<request_id>/decline")
@require_auth
def decline_friend_request(request_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM friends WHERE id = ? AND addressee_id = ?", (request_id, request.user["id"])
    ).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "That friend request no longer exists."}), 404
    conn.execute("DELETE FROM friends WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Friend request declined."})


@app.delete("/api/friends/<other_user_id>")
@require_auth
def remove_friend(other_user_id):
    conn = get_connection()
    conn.execute(
        """DELETE FROM friends WHERE status = 'accepted' AND (
               (requester_id = ? AND addressee_id = ?) OR
               (requester_id = ? AND addressee_id = ?)
           )""",
        (request.user["id"], other_user_id, other_user_id, request.user["id"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Friend removed."})


# ---------------------------------------------------------------------------
# Bible studies, sessions, and study groups
# ---------------------------------------------------------------------------

@app.get("/api/bible-studies")
def get_bible_studies():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM bible_studies ORDER BY week ASC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/bible-studies/<study_id>/sessions")
def get_study_sessions(study_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM study_sessions WHERE study_id = ? ORDER BY session_number ASC",
        (study_id,),
    ).fetchall()
    conn.close()
    sessions = []
    for r in rows:
        sessions.append({
            "id": r["id"],
            "session_number": r["session_number"],
            "title": r["title"],
            "scripture_ref": r["scripture_ref"],
            "questions": [q for q in r["questions"].split("\n") if q.strip()],
        })
    return jsonify(sessions)


@app.post("/api/bible-studies/<study_id>/groups")
@require_auth
def create_study_group(study_id):
    body = request.get_json(force=True) or {}
    name = (body.get("name") or "").strip() or "Our study group"
    member_handles = body.get("member_handles") or []

    conn = get_connection()
    study = conn.execute("SELECT id FROM bible_studies WHERE id = ?", (study_id,)).fetchone()
    if not study:
        conn.close()
        return jsonify({"error": "That study doesn't exist."}), 404

    friend_handles = get_accepted_friend_handles(conn, request.user["id"])
    invalid = [h for h in member_handles if h.lower() not in friend_handles]
    if invalid:
        conn.close()
        return jsonify({"error": f"You can only add friends to a group. Not a friend yet: {', '.join(invalid)}"}), 400

    group_id = new_id()
    conn.execute(
        "INSERT INTO study_groups (id, study_id, name, creator_id, created_at) VALUES (?, ?, ?, ?, ?)",
        (group_id, study_id, name, request.user["id"], now_iso()),
    )
    conn.execute(
        "INSERT INTO study_group_members (group_id, user_id, handle) VALUES (?, ?, ?)",
        (group_id, request.user["id"], request.user["handle"]),
    )
    for h in member_handles:
        member = conn.execute("SELECT id, handle FROM users WHERE LOWER(handle) = LOWER(?)", (h,)).fetchone()
        if member:
            conn.execute(
                "INSERT OR IGNORE INTO study_group_members (group_id, user_id, handle) VALUES (?, ?, ?)",
                (group_id, member["id"], member["handle"]),
            )
    conn.commit()
    conn.close()
    return jsonify({"id": group_id, "name": name}), 201


@app.get("/api/bible-studies/<study_id>/groups")
@require_auth
def list_study_groups(study_id):
    conn = get_connection()
    groups = conn.execute(
        """SELECT g.* FROM study_groups g
           JOIN study_group_members m ON m.group_id = g.id
           WHERE g.study_id = ? AND m.user_id = ?""",
        (study_id, request.user["id"]),
    ).fetchall()

    out = []
    for g in groups:
        members = conn.execute(
            "SELECT user_id, handle FROM study_group_members WHERE group_id = ?", (g["id"],)
        ).fetchall()
        progress_rows = conn.execute(
            "SELECT session_id, user_id FROM study_group_progress WHERE group_id = ?", (g["id"],)
        ).fetchall()
        progress = {}
        for p in progress_rows:
            progress.setdefault(p["session_id"], []).append(p["user_id"])

        out.append({
            "id": g["id"],
            "name": g["name"],
            "members": [{"user_id": m["user_id"], "handle": m["handle"]} for m in members],
            "progress": progress,
        })
    conn.close()
    return jsonify(out)


@app.post("/api/study-groups/<group_id>/sessions/<session_id>/complete")
@require_auth
def toggle_group_session_complete(group_id, session_id):
    conn = get_connection()
    membership = conn.execute(
        "SELECT * FROM study_group_members WHERE group_id = ? AND user_id = ?",
        (group_id, request.user["id"]),
    ).fetchone()
    if not membership:
        conn.close()
        return jsonify({"error": "You're not part of that group."}), 403

    existing = conn.execute(
        "SELECT * FROM study_group_progress WHERE group_id = ? AND session_id = ? AND user_id = ?",
        (group_id, session_id, request.user["id"]),
    ).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM study_group_progress WHERE group_id = ? AND session_id = ? AND user_id = ?",
            (group_id, session_id, request.user["id"]),
        )
        completed = False
    else:
        conn.execute(
            "INSERT INTO study_group_progress (group_id, session_id, user_id, completed_at) VALUES (?, ?, ?, ?)",
            (group_id, session_id, request.user["id"], now_iso()),
        )
        completed = True

    conn.commit()
    conn.close()
    return jsonify({"completed": completed})


# Looks up real scripture text from bible-api.com, which serves several
# public-domain translations for free (default here: the World English
# Bible, "web" — public domain, so there's no copyright concern quoting it
# in full). No API key needed. Requires the server to have internet access.
def fetch_scripture(ref):
    """Returns {reference, text, translation} or {error} — shared by the
    manual lookup endpoint and the verse-of-the-day endpoint."""
    try:
        resp = requests.get(
            f"https://bible-api.com/{ref}",
            params={"translation": "web"},
            timeout=8,
        )
    except requests.RequestException:
        return {"error": "Couldn't reach the scripture service. Check your internet connection and try again."}

    if resp.status_code != 200:
        return {"error": "Couldn't find that passage. Double check the reference and try again."}

    data = resp.json()
    if data.get("error"):
        return {"error": "Couldn't find that passage. Double check the reference and try again."}

    return {
        "reference": data.get("reference", ref),
        "text": (data.get("text") or "").strip(),
        "translation": data.get("translation_name", "World English Bible"),
    }


@app.get("/api/scripture")
def get_scripture():
    ref = request.args.get("ref", "").strip()
    if not ref:
        return jsonify({"error": "Missing scripture reference."}), 400

    result = fetch_scripture(ref)
    if "error" in result:
        status = 502 if "internet connection" in result["error"] else 404
        return jsonify(result), status
    return jsonify(result)


# Verse of the day — picks a reference from votd_verses deterministically
# from today's date (day-of-year modulo the list length), so everyone sees
# the same verse all day and it changes tomorrow.
@app.get("/api/verse-of-day")
def get_verse_of_day():
    conn = get_connection()
    verses = conn.execute("SELECT * FROM votd_verses ORDER BY id").fetchall()
    conn.close()

    if not verses:
        return jsonify({"error": "No verses configured yet."}), 404

    today = datetime.now(timezone.utc).date()
    index = today.timetuple().tm_yday % len(verses)
    ref = verses[index]["reference"]

    result = fetch_scripture(ref)
    result["date"] = today.isoformat()
    if "error" in result:
        status = 502 if "internet connection" in result["error"] else 404
        return jsonify(result), status
    return jsonify(result)


@app.get("/api/affirmations")
def get_affirmations():
    conn = get_connection()
    rows = conn.execute("SELECT text FROM affirmations").fetchall()
    conn.close()
    return jsonify([r["text"] for r in rows])


# ---------------------------------------------------------------------------
# Mood Help — articles, tap-an-emoji comfort, and private journal
# ---------------------------------------------------------------------------

@app.get("/api/mood-help")
def get_mood_help():
    struggle = request.args.get("struggle")
    conn = get_connection()
    if struggle:
        rows = conn.execute(
            "SELECT * FROM mood_help WHERE LOWER(struggle) = LOWER(?)", (struggle,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM mood_help").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.get("/api/mood-emojis")
def get_mood_emojis():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM mood_emojis").fetchall()
    conn.close()
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "emoji": r["emoji"],
            "label": r["label"],
            "messages": [m for m in r["messages"].split("\n") if m.strip()],
            "verses": [v for v in (r["verses"] or "").split("\n") if v.strip()],
        })
    return jsonify(out)


@app.get("/api/mood-journal")
@require_auth
def get_mood_journal():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM mood_journal WHERE user_id = ? ORDER BY created_at DESC",
        (request.user["id"],),
    ).fetchall()
    conn.close()
    return jsonify([{
        "id": r["id"], "emoji": r["emoji"], "label": r["label"],
        "note": r["note"], "created_at": r["created_at"],
    } for r in rows])


@app.post("/api/mood-journal")
@require_auth
def post_mood_journal():
    body = request.get_json(force=True) or {}
    emoji = body.get("emoji") or ""
    label = body.get("label") or ""
    note = (body.get("note") or "").strip()

    if not note:
        return jsonify({"error": "Write a little about how you're feeling first."}), 400
    if len(note) > 2000:
        return jsonify({"error": "Keep it under 2000 characters."}), 400

    entry_id = new_id()
    conn = get_connection()
    conn.execute(
        "INSERT INTO mood_journal (id, user_id, emoji, label, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (entry_id, request.user["id"], emoji, label, note, now_iso()),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": entry_id}), 201


@app.delete("/api/mood-journal/<entry_id>")
@require_auth
def delete_mood_journal(entry_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM mood_journal WHERE id = ? AND user_id = ?", (entry_id, request.user["id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Deleted."})


# ---------------------------------------------------------------------------
# Prayer wall
# ---------------------------------------------------------------------------

@app.get("/api/prayer-wall")
def get_prayer_wall():
    conn = get_connection()
    posts = conn.execute(
        "SELECT * FROM prayer_wall WHERE hidden = 0 ORDER BY created_at DESC"
    ).fetchall()

    out = []
    for p in posts:
        count = conn.execute(
            "SELECT COUNT(*) as n FROM prayer_reactions WHERE post_id = ?", (p["id"],)
        ).fetchone()["n"]
        out.append({
            "id": p["id"],
            "content": p["content"],
            "handle": "anonymous" if p["anonymous"] else p["handle"],
            "prayed_count": count,
            "created_at": p["created_at"],
        })
    conn.close()
    return jsonify(out)


@app.post("/api/prayer-wall")
@require_auth
def post_prayer():
    body = request.get_json(force=True) or {}
    content = (body.get("content") or "").strip()
    anonymous = 1 if body.get("anonymous") else 0

    if not content:
        return jsonify({"error": "Say a little about what you'd like prayer for."}), 400
    if len(content) > 800:
        return jsonify({"error": "Keep it under 800 characters."}), 400

    post_id = new_id()
    conn = get_connection()
    conn.execute(
        "INSERT INTO prayer_wall (id, user_id, handle, content, anonymous, hidden, created_at) VALUES (?, ?, ?, ?, ?, 0, ?)",
        (post_id, request.user["id"], request.user["handle"], content, anonymous, now_iso()),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": post_id}), 201


@app.post("/api/prayer-wall/<post_id>/pray")
@require_auth
def pray_for(post_id):
    conn = get_connection()
    post = conn.execute("SELECT * FROM prayer_wall WHERE id = ?", (post_id,)).fetchone()
    if not post:
        conn.close()
        return jsonify({"error": "That post no longer exists."}), 404

    user_id = request.user["id"]
    existing = conn.execute(
        "SELECT * FROM prayer_reactions WHERE post_id = ? AND user_id = ?", (post_id, user_id)
    ).fetchone()

    if existing:
        conn.execute(
            "DELETE FROM prayer_reactions WHERE post_id = ? AND user_id = ?", (post_id, user_id)
        )
        praying = False
    else:
        conn.execute(
            "INSERT INTO prayer_reactions (post_id, user_id) VALUES (?, ?)", (post_id, user_id)
        )
        praying = True
        if post["user_id"] != user_id:
            notify(conn, post["user_id"], "prayer", f"{request.user['handle']} prayed for your prayer request.")

    conn.commit()
    count = conn.execute(
        "SELECT COUNT(*) as n FROM prayer_reactions WHERE post_id = ?", (post_id,)
    ).fetchone()["n"]
    conn.close()
    return jsonify({"prayed_count": count, "praying": praying})


# ---------------------------------------------------------------------------
# The Gist (casual board) — supports tagging friends and reacting to posts
# ---------------------------------------------------------------------------

REACTION_TYPES = ["thumbs_up", "love", "sad", "pray", "clap"]


@app.get("/api/gist")
@optional_auth
def get_gist():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM gist WHERE hidden = 0 ORDER BY created_at ASC"
    ).fetchall()

    out = []
    for m in rows:
        reaction_rows = conn.execute(
            "SELECT reaction, COUNT(*) as n FROM gist_reactions WHERE message_id = ? GROUP BY reaction",
            (m["id"],),
        ).fetchall()
        counts = {rt: 0 for rt in REACTION_TYPES}
        for rr in reaction_rows:
            if rr["reaction"] in counts:
                counts[rr["reaction"]] = rr["n"]

        my_reaction = None
        if request.user:
            mine = conn.execute(
                "SELECT reaction FROM gist_reactions WHERE message_id = ? AND user_id = ?",
                (m["id"], request.user["id"]),
            ).fetchone()
            if mine:
                my_reaction = mine["reaction"]

        out.append({
            "id": m["id"],
            "handle": m["handle"],
            "content": m["content"],
            "created_at": m["created_at"],
            "tags": [t for t in (m["tagged_handles"] or "").split(",") if t],
            "reactions": counts,
            "my_reaction": my_reaction,
        })
    conn.close()
    return jsonify(out)


@app.post("/api/gist")
@require_auth
def post_gist():
    body = request.get_json(force=True) or {}
    content = (body.get("content") or "").strip()
    requested_tags = body.get("tags") or []

    if not content:
        return jsonify({"error": "Write something first."}), 400
    if len(content) > 500:
        return jsonify({"error": "Keep it under 500 characters."}), 400

    conn = get_connection()
    friend_handles = get_accepted_friend_handles(conn, request.user["id"])
    valid_tags = [t for t in requested_tags if t.lower() in friend_handles]

    msg_id = new_id()
    conn.execute(
        "INSERT INTO gist (id, user_id, handle, content, hidden, created_at, tagged_handles) VALUES (?, ?, ?, ?, 0, ?, ?)",
        (msg_id, request.user["id"], request.user["handle"], content, now_iso(), ",".join(valid_tags)),
    )
    conn.commit()
    conn.close()
    return jsonify({"id": msg_id}), 201


@app.post("/api/gist/<message_id>/react")
@require_auth
def react_to_gist(message_id):
    body = request.get_json(force=True) or {}
    reaction = body.get("reaction")
    if reaction not in REACTION_TYPES:
        return jsonify({"error": "That's not a valid reaction."}), 400

    conn = get_connection()
    msg = conn.execute("SELECT id, user_id FROM gist WHERE id = ?", (message_id,)).fetchone()
    if not msg:
        conn.close()
        return jsonify({"error": "That message no longer exists."}), 404

    existing = conn.execute(
        "SELECT reaction FROM gist_reactions WHERE message_id = ? AND user_id = ?",
        (message_id, request.user["id"]),
    ).fetchone()

    if existing and existing["reaction"] == reaction:
        conn.execute(
            "DELETE FROM gist_reactions WHERE message_id = ? AND user_id = ?",
            (message_id, request.user["id"]),
        )
        my_reaction = None
    else:
        conn.execute(
            """INSERT INTO gist_reactions (message_id, user_id, reaction) VALUES (?, ?, ?)
               ON CONFLICT(message_id, user_id) DO UPDATE SET reaction = excluded.reaction""",
            (message_id, request.user["id"], reaction),
        )
        my_reaction = reaction
        if msg["user_id"] != request.user["id"]:
            icon = {"thumbs_up": "👍", "love": "❤️", "sad": "😢", "pray": "🙏", "clap": "👏"}.get(reaction, "")
            notify(conn, msg["user_id"], "reaction", f"{request.user['handle']} reacted {icon} to your Gist post.")

    conn.commit()
    counts = {}
    for rt in REACTION_TYPES:
        n = conn.execute(
            "SELECT COUNT(*) as n FROM gist_reactions WHERE message_id = ? AND reaction = ?",
            (message_id, rt),
        ).fetchone()["n"]
        counts[rt] = n
    conn.close()
    return jsonify({"reactions": counts, "my_reaction": my_reaction})


# ---------------------------------------------------------------------------
# Moderation reports
# ---------------------------------------------------------------------------

@app.post("/api/reports")
@require_auth
def report_post():
    body = request.get_json(force=True) or {}
    board = body.get("board")
    post_id = body.get("post_id")
    reason = body.get("reason")

    if not board or not post_id or not reason:
        return jsonify({"error": "Missing report details."}), 400

    conn = get_connection()
    conn.execute(
        "INSERT INTO reports (id, board, post_id, reason, reported_by, status, created_at) VALUES (?, ?, ?, ?, ?, 'open', ?)",
        (new_id(), board, post_id, reason, request.user["id"], now_iso()),
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Thanks — a moderator will review this."}), 201


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

@app.get("/api/notifications")
@require_auth
def get_notifications():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 30",
        (request.user["id"],),
    ).fetchall()
    unread = conn.execute(
        "SELECT COUNT(*) as n FROM notifications WHERE user_id = ? AND read = 0", (request.user["id"],)
    ).fetchone()["n"]
    conn.close()
    return jsonify({
        "unread_count": unread,
        "notifications": [{
            "id": r["id"], "type": r["type"], "message": r["message"],
            "read": bool(r["read"]), "created_at": r["created_at"],
        } for r in rows],
    })


@app.post("/api/notifications/<notif_id>/read")
@require_auth
def mark_notification_read(notif_id):
    conn = get_connection()
    conn.execute(
        "UPDATE notifications SET read = 1 WHERE id = ? AND user_id = ?", (notif_id, request.user["id"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Marked as read."})


@app.post("/api/notifications/read-all")
@require_auth
def mark_all_notifications_read():
    conn = get_connection()
    conn.execute("UPDATE notifications SET read = 1 WHERE user_id = ?", (request.user["id"],))
    conn.commit()
    conn.close()
    return jsonify({"message": "All marked as read."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(host="0.0.0.0", port=port, debug=True)
