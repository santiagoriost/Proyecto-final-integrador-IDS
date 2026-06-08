document.getElementById("buscarHistorial").addEventListener("input", filtrar);

document.querySelectorAll(".custom-select").forEach(sel => {
    sel.querySelector(".custom-select-btn").addEventListener("click", () => {
        sel.classList.toggle("open");
    });
    sel.querySelectorAll(".custom-options button").forEach(btn => {
        btn.addEventListener("click", () => {
            sel.querySelector(".custom-select-text").textContent = btn.textContent;
            sel.classList.remove("open");
            filtrar();
        });
    });
});

document.addEventListener("click", e => {
    document.querySelectorAll(".custom-select.open").forEach(sel => {
        if (!sel.contains(e.target)) sel.classList.remove("open");
    });
});

function filtrar() {
    const texto = document.getElementById("buscarHistorial").value.toLowerCase();
    const tipoEl = document.querySelector(".custom-select[data-filter='tipo'] .custom-select-text");
    const tipo = tipoEl ? tipoEl.textContent.trim() : "Todos los tipos";

    document.querySelectorAll("#tablaHistorial tbody tr[data-tipo]").forEach(fila => {
        const accion  = fila.querySelector("td:nth-child(3)")?.textContent.toLowerCase() || "";
        const detalle = fila.querySelector("td:nth-child(4)")?.textContent.toLowerCase() || "";
        const filaTipo = fila.dataset.tipo;

        const coincideTexto = accion.includes(texto) || detalle.includes(texto);
        const coincideTipo  = tipo === "Todos los tipos" || filaTipo === tipo.toLowerCase();

        fila.style.display = coincideTexto && coincideTipo ? "" : "none";
    });
}