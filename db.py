import sqlite3
from models import create_tables

DATABASE = "users.db"

def get_connection():
    """
    Retourne une connexion SQLite avec accès par nom de colonne.
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialise la base de données si nécessaire.
    """
    create_tables()
