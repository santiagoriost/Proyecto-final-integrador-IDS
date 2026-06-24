const select = document.getElementById("selectPuntuacion");
const boton = select.querySelector(".select-boton");
const opciones = select.querySelectorAll(".select-opcion");
const texto = select.querySelector(".select-texto");
const input = document.getElementById("puntuacionInput");
/* boton seleccionar opciones*/
boton.addEventListener("click", () => {
    select.classList.toggle("active");
});
opciones.forEach(opcion => {
    opcion.addEventListener("click", () => {
        texto.textContent = opcion.textContent;
        input.value = opcion.dataset.value;
        select.classList.remove("active");
    });
});
document.addEventListener("click", (e) => {
    if (!select.contains(e.target)) {
        select.classList.remove("active");
    }
});
/* boton eliminar resena*/
