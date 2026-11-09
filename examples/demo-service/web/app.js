// Application de démonstration, non minifiée.
const form = document.getElementById("form");
const status = document.getElementById("status");
const list = document.getElementById("list");
const refresh = document.getElementById("refresh");

function render(rows) {
  list.innerHTML = "";
  for (const row of rows) {
    const li = document.createElement("li");
    li.textContent = row.name + " — " + row.created_at;
    list.appendChild(li);
  }
}

async function load() {
  console.log("chargement des présences");
  const response = await fetch("/api/consultation");
  const data = await response.json();
  render(data.rows);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = form.querySelector("input").value;
  await fetch("/api/emargement?name=" + encodeURIComponent(name));
  status.textContent = "Émargement enregistré.";
  await load();
});

refresh.addEventListener("click", load);

// TODO: remplacer le polling par une action utilisateur.
setInterval(load, 5000);
load();
