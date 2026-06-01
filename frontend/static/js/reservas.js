flatpickr("input[type='date']", {
    dateFormat: "d/m/Y",
    minDate: "today",
    disableMobile: true
});
const cajaHora = document.getElementById("hora-box");
const entradaHora = document.getElementById("hora-input");
const scrollHoras = document.getElementById("hora-scroll");
const scrollMinutos = document.getElementById("minuto-scroll");
let horaSeleccionada = "08";
let minutoSeleccionado = "00";
for (let hora = 8; hora <= 22; hora++) {
    const botonHora = document.createElement("button");
    botonHora.type = "button";
    botonHora.className = "item-hora";
    botonHora.textContent = String(hora).padStart(2, "0");
    botonHora.addEventListener("click", () => {
        horaSeleccionada = botonHora.textContent;
        actualizarHora();
    });
    scrollHoras.appendChild(botonHora);
}
for (let minuto = 0; minuto <= 55; minuto += 5) {
    const botonMinuto = document.createElement("button");
    botonMinuto.type = "button";
    botonMinuto.className = "item-minuto";
    botonMinuto.textContent = String(minuto).padStart(2, "0");

    botonMinuto.addEventListener("click", () => {
        minutoSeleccionado = botonMinuto.textContent;
        actualizarHora();
    });
    scrollMinutos.appendChild(botonMinuto);
}
function actualizarHora() {
    entradaHora.value = `${horaSeleccionada}:${minutoSeleccionado}`;
    document.querySelectorAll(".item-hora").forEach(item => {
        item.classList.toggle("active", item.textContent === horaSeleccionada);
    });
    document.querySelectorAll(".item-minuto").forEach(item => {
        item.classList.toggle("active", item.textContent === minutoSeleccionado);
    });
}
entradaHora.addEventListener("click", () => {
    cajaHora.classList.toggle("active");
});
document.addEventListener("click", (evento) => {
    if (!cajaHora.contains(evento.target)) {
        cajaHora.classList.remove("active");
    }
});
actualizarHora();
const selectReserva = document.getElementById("select-reserva");
const botonSelect = selectReserva.querySelector(".select-boton");
const textoTipoReserva = document.getElementById("texto-tipo-reserva");
const inputTipoReserva = document.getElementById("tipo-reserva");
const opcionesReserva = selectReserva.querySelectorAll(".select-opcion");
botonSelect.addEventListener("click", () => {
    selectReserva.classList.toggle("active");
});
opcionesReserva.forEach(opcion => {
    opcion.addEventListener("click", () => {
        const valor = opcion.dataset.value;
        const texto = opcion.textContent;

        inputTipoReserva.value = valor;
        textoTipoReserva.textContent = texto;

        opcionesReserva.forEach(item => item.classList.remove("active"));
        opcion.classList.add("active");

        selectReserva.classList.remove("active");
    });
});
document.addEventListener("click", (evento) => {
    if (!selectReserva.contains(evento.target)) {
        selectReserva.classList.remove("active");
    }
});