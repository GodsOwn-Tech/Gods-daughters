"""
auth.py — password hashing and JWT tokens.

Handles are public (shown on posts). Email/password are private — used
only for login and, if needed, moderation contact.
"""
import os
import jwt
import bcrypt
import datetime
from functools import wraps
from flask import request, jsonify

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def make_token(user_id, handle):
    payload = {
        "id": user_id,
        "handle": handle,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def require_auth(f):
    """Decorator: blocks the request unless a valid Bearer token is present.
    Attaches the decoded payload to request.user = {id, handle}."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "You need to be signed in for that."}), 401
        token = header.split(" ", 1)[1]
        try:
            request.user = decode_token(token)
        except jwt.PyJWTError:
            return jsonify({"error": "Your session expired. Please sign in again."}), 401
        return f(*args, **kwargs)
    return wrapper


def optional_auth(f):
    """Decorator: attaches request.user if a valid token is present
    (otherwise request.user = None), but never blocks the request.
    Useful for endpoints like the gist feed, which behave slightly
    differently when the visitor is logged in (e.g. showing which
    reaction they've already picked) but are still visible to everyone."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        request.user = None
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header.split(" ", 1)[1]
            try:
                request.user = decode_token(token)
            except jwt.PyJWTError:
                pass
        return f(*args, **kwargs)
    return wrapper
