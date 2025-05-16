import sqlite3
from flask import request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash

DATABASE = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def authenticate_user(username, password):
    """
    Vérifie les identifiants utilisateur et initialise la session si valide.
    """
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["poste"] = user["poste"]
        session["role"] = user["role"]
        return True
    return False

def logout_user():
    """
    Déconnecte l'utilisateur en supprimant la session.
    """
    session.clear()

def get_current_user():
    """
    Récupère l'utilisateur actuellement connecté (dict) ou None.
    """
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "username": session["username"],
        "poste": session["poste"],
        "role": session["role"]
    }

def login_required(func):
    """
    Décorateur pour restreindre l'accès aux routes à un utilisateur connecté.
    """
    from functools import wraps
    @wraps(func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Connexion requise", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapped
