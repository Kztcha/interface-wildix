let formulaireOuvert = false;
let enrichissements = {};
let userSession = {};

// Connexion WebSocket
console.log("📡 Tentative de connexion WebSocket...");
const socket = io();

socket.on("connect", () => {
  console.log("✅ WebSocket connecté !");
});

socket.on("connect_error", (err) => {
  console.error("❌ Erreur WebSocket :", err);
});

socket.on("enrichissement_updated", () => {
  if (!formulaireOuvert) {
    console.log("🔁 Mise à jour reçue → rechargement automatique");
    window.location.reload();
  } else {
    console.warn("⚠️ JSON modifié pendant une édition. Recharge différée.");
    showReloadBanner();
  }
});

function showReloadBanner() {
  let banner = document.getElementById("reloadBanner");

  if (!banner) {
    banner = document.createElement("div");
    banner.id = "reloadBanner";
    banner.style.position = "fixed";
    banner.style.top = "0";
    banner.style.left = "0";
    banner.style.right = "0";
    banner.style.backgroundColor = "#ffcc00";
    banner.style.color = "#000";
    banner.style.padding = "10px";
    banner.style.textAlign = "center";
    banner.style.zIndex = "9999";
    banner.innerHTML = `
      ⚠️ Des données ont été modifiées sur le serveur.
      <button onclick="window.location.reload()">Recharger maintenant</button>
    `;
    document.body.prepend(banner);
  }
}

// Chargement de la session utilisateur
function loadSessionInfo() {
  fetch("/session-info")
    .then(res => res.json())
    .then(data => {
      userSession = data;
    });
}

// Chargement des appels depuis l'API dynamique
function loadCalls() {
  fetch("/appels")
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#callTable tbody");
      tbody.innerHTML = "";

      data.result.records.forEach(call => {
        const tr = document.createElement("tr");
        tr.setAttribute("data-id", call.id);

        const enrich = enrichissements[call.id] || {};
        let statut = "";

        if (enrich.reponduParAgent) {
          statut = "✔ Répondu";
        } else if (enrich.traiteParOuTransmisA === userSession.username) {
          statut = "📨 Reçu (transmis)";
        } else if (enrich.reponduParAgent === false && enrich.traiteParOuTransmisA) {
          statut = `🔁 Transmis à ${enrich.traiteParOuTransmisA}`;
        }

        tr.innerHTML = `
          <td class="start">${call.start}</td>
          <td class="from">${call.from_number}</td>
          <td class="to">${call.to_number}</td>
          <td class="duration">${call.duration}</td>
          <td class="disposition">${call.disposition} ${statut}</td>
          <td>
            <button onclick="openForm('${call.id}')">Enrichir</button>
            <div class="info-supplementaire" id="enrich-${call.id}"></div>
          </td>
        `;
        tbody.appendChild(tr);
      });

      updateTableWithEnrichissements();
    });
}

function loadEnrichissements() {
  fetch("/enrichissements")
    .then(res => res.json())
    .then(data => {
      enrichissements = data;
      updateTableWithEnrichissements();
    });
}

function updateTableWithEnrichissements() {
  Object.keys(enrichissements).forEach(callId => {
    const div = document.getElementById(`enrich-${callId}`);
    const data = enrichissements[callId];

    if (div) {
      div.innerHTML = `
        <small>
          ${data.date || ""} ${data.heure || ""}<br/>
          <b>${data.modeAccueil || ""}</b> - ${data.objet || ""}<br/>
          ${data.commentaireObjet || ""}<br/>
          <i>${data.resultat || ""} → ${data.orientation || ""}</i><br/>
          Répondu : ${data.reponduParAgent ? "oui" : "non"}<br/>
          Transmis à : ${data.traiteParOuTransmisA || "-"}<br/>
          <span>${data.commentaireResultat || ""}</span>
        </small>
      `;
    }
  });
}

function openForm(callId) {
  formulaireOuvert = true;
  document.getElementById("formContainer").classList.remove("hidden");
  document.getElementById("callId").value = callId;

  const now = new Date();
  document.getElementById("dateAuto").textContent = now.toLocaleDateString();
  document.getElementById("heureAuto").textContent = now.toLocaleTimeString();

  const e = enrichissements[callId] || {};
  document.getElementById("modeAccueil").value = e.modeAccueil || "";
  document.getElementById("objet").value = e.objet || "";
  document.getElementById("commentaireObjet").value = e.commentaireObjet || "";
  document.getElementById("resultat").value = e.resultat || "";
  document.getElementById("orientation").value = e.orientation || "";
  document.getElementById("reponduParAgent").checked = e.reponduParAgent || false;
  document.getElementById("traiteParOuTransmisA").value = e.traiteParOuTransmisA || "";
  document.getElementById("commentaireResultat").value = e.commentaireResultat || "";

  toggleTraiteParOuTransmisA();
}

function closeForm() {
  formulaireOuvert = false;
  document.getElementById("formContainer").classList.add("hidden");
}

document.getElementById("enrichForm").addEventListener("submit", function(e) {
  e.preventDefault();

  const callId = document.getElementById("callId").value;
  const update = {};
  update[callId] = {
    date: document.getElementById("dateAuto").textContent,
    heure: document.getElementById("heureAuto").textContent,
    modeAccueil: document.getElementById("modeAccueil").value,
    objet: document.getElementById("objet").value,
    commentaireObjet: document.getElementById("commentaireObjet").value,
    resultat: document.getElementById("resultat").value,
    orientation: document.getElementById("orientation").value,
    reponduParAgent: document.getElementById("reponduParAgent").checked,
    traiteParOuTransmisA: document.getElementById("traiteParOuTransmisA").value,
    commentaireResultat: document.getElementById("commentaireResultat").value
  };

  fetch("/enrichissements", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update)
  }).then(() => {
    closeForm();
  });
});

function toggleTraiteParOuTransmisA() {
  const checkbox = document.getElementById("reponduParAgent");
  const champ = document.getElementById("traiteParOuTransmisA");
  champ.disabled = checkbox.checked;
}

// Initialisation
loadSessionInfo();
loadEnrichissements();
loadCalls();
