const buscarResena = document.getElementById("buscarResena");
const tablaResenas = document.getElementById("tablaResenas");
const customSelect = document.querySelector(".custom-select[data-filter='puntuacion']");
const customBtn = customSelect.querySelector(".custom-select-btn");
const customText = customSelect.querySelector(".custom-select-text");
const customOptions = customSelect.querySelectorAll(".custom-options button");
const modalEliminar = document.getElementById("modalEliminar");
const formEliminar = document.getElementById("formEliminar");
const btnCancelar = document.getElementById("btnCancelar");

let filtroPuntuacion = "todos";

customBtn.addEventListener("click", () => {
    customSelect.classList.toggle("open");
});

customOptions.forEach(option => {
    option.addEventListener("click", () => {
        filtroPuntuacion = option.dataset.value;
        customText.textContent = option.textContent;
        customSelect.classList.remove("open");
        filtrar();
    });
});

document.addEventListener("click", (e) => {
    if (!customSelect.contains(e.target)) {
        customSelect.classList.remove("active");
    }
});

buscarResena.addEventListener("input", filtrar);

function filtrar() {
    const texto = buscarResena.value.toLowerCase();
    const filas = tablaResenas.querySelectorAll("tbody tr");

    filas.forEach(fila => {
        const comentario = fila.children[4]?.textContent.toLowerCase() || "";
        const puntuacion = fila.dataset.puntuacion;

        const coincideTexto = comentario.includes(texto);
        const coincidePuntuacion = filtroPuntuacion === "todos" || puntuacion === filtroPuntuacion;

        fila.style.display = coincideTexto && coincidePuntuacion ? "" : "none";
    });
}

document.querySelectorAll(".btn-eliminar").forEach(btn => {
    btn.addEventListener("click", () => {
        formEliminar.action = btn.dataset.url;
        modalEliminar.style.display = "flex";
    });
});

btnCancelar.addEventListener("click", () => {
    modalEliminar.style.display = "none";
});

modalEliminar.addEventListener("click", (e) => {
    if (e.target === modalEliminar) {
        modalEliminar.style.display = "none";
    }
});