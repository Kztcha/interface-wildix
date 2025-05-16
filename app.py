from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, render_template, session
from flask_socketio import SocketIO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import json
import time
from auth import authenticate_user, logout_user, get_current_user, login_required
from db import init_db

# ------------------------------------------------------------------------------
# Initialisation
# ------------------------------------------------------------------------------

app = Flask(__name__, static_folder='static')
app.secret_key = 'votre-cle-secrete-a-remplacer'
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------------------------------------------------------
# Fichiers JSON (simulation)
# ------------------------------------------------------------------------------

ENRICH_FILE = os.path.join(app.static_folder, 'mock', 'enrichissements.json')
CALL_FILE = os.path.join(app.static_folder, 'mock', 'call_history.json')

# ------------------------------------------------------------------------------
# ROUTES FRONT
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    if "user_id" not in session:
        return redirect("/login")
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if authenticate_user(username, password):
            return redirect("/")
        return "Identifiants invalides", 401
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/login")

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ------------------------------------------------------------------------------
# API JSON SIMULÉ : appels et enrichissements
# ------------------------------------------------------------------------------

@app.route('/enrichissements', methods=['GET'])
def get_enrichissements():
    if not os.path.exists(ENRICH_FILE):
        return jsonify({})
    with open(ENRICH_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/enrichissements', methods=['POST'])
def save_enrichissement():
    new_data = request.json
    if not os.path.exists(ENRICH_FILE):
        data = {}
    else:
        with open(ENRICH_FILE, 'r') as f:
            data = json.load(f)
    data.update(new_data)
    with open(ENRICH_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({"status": "success", "data": data})

@app.route('/appels', methods=['GET'])
def get_appels():
    """
    Renvoie les appels :
    - tous si admin
    - ou selon poste
    - ou si transmis à l'utilisateur via enrichissements.json
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "Non connecté"}), 401

    poste = user["poste"]
    username = user["username"]

    appels_result = []

    if not os.path.exists(CALL_FILE):
        return jsonify({"result": {"records": []}})

    with open(CALL_FILE, 'r') as f:
        data = json.load(f)
    appels = data["result"]["records"]

    if user["role"] == "admin":
        return jsonify(data)

    # charger enrichissements
    enrichissements = {}
    if os.path.exists(ENRICH_FILE):
        with open(ENRICH_FILE, 'r') as f:
            enrichissements = json.load(f)

    for appel in appels:
        id_appel = appel.get("id")
        match_poste = (
            appel.get("from_number") == poste or
            appel.get("to_number") == poste or
            (appel.get("channel") and f"SIP/{poste}-" in appel.get("channel")) or
            (appel.get("dstchannel") and f"SIP/{poste}-" in appel.get("dstchannel"))
        )
        transmis_a_utilisateur = (
            id_appel in enrichissements and
            enrichissements[id_appel].get("traiteParOuTransmisA") == username
        )

        if match_poste or transmis_a_utilisateur:
            appels_result.append(appel)

    return jsonify({
        "type": "result",
        "result": {
            "total": len(appels_result),
            "records": appels_result
        }
    })

@app.route('/session-info')
def session_info():
    user = get_current_user()
    if not user:
        return jsonify({})
    return jsonify({
        "username": user["username"],
        "role": user["role"],
        "poste": user["poste"]
    })

# ------------------------------------------------------------------------------
# WATCHDOG TEMPS RÉEL
# ------------------------------------------------------------------------------

class EnrichissementChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print("📁 Événement détecté :", event.event_type, "-", event.src_path)
        filename = os.path.basename(event.src_path)
        if filename in ["enrichissements.json", "call_history.json"]:
            time.sleep(0.1)
            print(f"🚀 {filename} modifié → on notifie les clients")
            socketio.emit("enrichissement_updated")

def start_watcher():
    handler = EnrichissementChangeHandler()
    observer = Observer()
    observer.schedule(handler, path=os.path.dirname(ENRICH_FILE), recursive=False)
    observer.start()

# ------------------------------------------------------------------------------
# DÉMARRAGE APP
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    watcher_thread = threading.Thread(target=start_watcher, daemon=True)
    watcher_thread.start()
    socketio.run(app, debug=True)
