import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "users.db"

def create_tables():
    """
    Crée la table des utilisateurs si elle n'existe pas.
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            poste TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user'
        )
    """)

    conn.commit()
    conn.close()

def add_user(username, password, poste, role="user"):
    """
    Ajoute un utilisateur à la base (mot de passe hashé).
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    password_hash = generate_password_hash(password)
    try:
        c.execute("""
            INSERT INTO users (username, password_hash, poste, role)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, poste, role))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ Utilisateur '{username}' déjà existant.")
    finally:
        conn.close()

def get_all_users():
    """
    Retourne la liste de tous les utilisateurs.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return users
