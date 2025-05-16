from db import init_db
from models import add_user

# Initialise la base et crée la table users si elle n'existe pas
init_db()

# Ajoute des utilisateurs
add_user("admin", "adminpass", "0000", role="admin")     # admin générique
add_user("alice", "alicepass", "33", role="user")        # poste fictif
add_user("bob", "bobpass", "44", role="user")            # poste fictif
add_user("kernel", "kernelpass", "11", role="user")      # poste lié à appel n°68

print("✅ Base users.db initialisée avec 4 comptes.")
