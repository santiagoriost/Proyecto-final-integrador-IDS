const buscarResena = document.getElementById("buscarResena");
const tablaResenas = document.getElementById("tablaResenas");
const customSelect = document.querySelector(".custom-select[data-filter='puntuacion']");
const customBtn = customSelect.querySelector(".custom-select-btn");
const customText = customSelect.querySelector(".custom-select-text");
const customOptions = customSelect.querySelectorAll(".custom-options button");

let filtroPuntuacion = "todos";

customBtn.addEventListener("click", () => {
    customSelect.classList.toggle("active");
});

customOptions.forEach(option => {
    option.addEventListener("click", () => {
        filtroPuntuacion = option.dataset.value;
        customText.textContent = option.textContent;
        customSelect.classList.remove("active");
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