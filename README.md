Cette application a été fait en grande partie a l'aide de chat gpt basé sur mon application qui était statique, 
chat gpt a ajouter le rafraichissement dynamique et la notion de transfert, incluant la modification du fonctionnement origianl des db

librairie un peu spécial

| Composant                  | Description                                                   |
| -------------------------- | ------------------------------------------------------------- |
| **Flask-SocketIO**         | Communication temps réel (mise à jour automatique)            |
https://flask-socketio.readthedocs.io/en/latest/
| **Watchdog**               | Détecte toute modification des fichiers JSON                  |
https://python-watchdog.readthedocs.io/en/stable/index.html

---

### 👤 Authentification & utilisateurs

voir init_db.py

* Les utilisateurs se connectent via un **formulaire HTML** (`login.html`)
* L’authentification se fait via une **base SQLite**
* Chaque utilisateur a un **poste Wildix**,mais j'ai pris un id que j'ai trouve dans le json exemple en réalité je ne sais pas si il s'agit de l'id correct
 mais vu que tout le code est basé dessus en terme de fonctionnement purement et simplement on verra pas la différence
* Un compte **admin** voit **tous les appels**
* Les autres utilisateurs voient :

  * les appels **associés à leur poste**
  * les appels **qui leur ont été transmis et qu'ils ont transmis**

---

### 📂 Structure des fichiers

```
wildix-app/
├── app.py                → Serveur principal Flask + SocketIO
├── auth.py               → Gestion des sessions, login/logout
├── db.py                 → Connexion SQLite + init
├── models.py             → Définition de la table `users`
├── init_db.py            → Script pour créer la base et ajouter des utilisateurs
├── users.db              → Base SQLite
│
├── static/
│   ├── index.html        → Interface principale
│   ├── login.html        → Page de connexion (statique)
│   ├── script.js         → Logique d'affichage, socket, formulaire
│   ├── style.css         → Styles visuels
│   └── mock/
│       ├── call_history.json       → Simulation des appels (structure Wildix)
│       └── enrichissements.json    → Enrichissements enregistrés dynamiquement
```

---

### 🔁 Fonctionnalités principales

#### 1. 📞 Chargement des appels (`/appels`)

* Appels lus depuis `call_history.json`
* Si `admin` → tout
* Sinon → filtrés selon :

  * `from_number`
  * `to_number`
  * `channel`
  * `dstchannel`
  * ou `traiteParOuTransmisA == user`

#### 2. 📝 Enrichissement

* Formulaire affiché par ligne
* Ajout d'informations :

  * date, heure
  * objet, résultat
  * `reponduParAgent` (checkbox)
  * `traiteParOuTransmisA` (si transfert)
* Enregistré dans `enrichissements.json`

#### 3. 🔄 Temps réel

* Modif fichier JSON → événement WebSocket
* Client JS met à jour automatiquement

---

### ⚠️ Règles métier

* Si `reponduParAgent` est coché :

  * champ "Transmis à" désactivé
* Si non coché :

  * utilisateur saisit le **nom utilisateur** cible du transfert (pas le poste)

---





l'ajout d'utilisateur est manuelle ,il y a zéro sécurité réel sur les logins , l'interface web n'est pas conçu pour gérer énormément d'email 
(pas de bug visuel ou autre , juste pas ergonomique)
