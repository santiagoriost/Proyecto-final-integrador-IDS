let reservaAEliminar = null;

const modalEliminar = document.getElementById("modalEliminar");
const btnCancelarModal = document.getElementById("btnCancelarModal");
const btnConfirmarEliminar = document.getElementById("btnConfirmarEliminar");

const inputBusqueda = document.querySelector(".filter-search input");
const btnFiltro = document.querySelector(".btn-filtro");
const filasReservas = document.querySelectorAll(".reservas-table tbody tr");

let estadoSeleccionado = "Todos los estados";
let tipoSeleccionado = "Todos los tipos";

function normalizarTexto(texto) {
    return texto
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .trim();
}

function aplicarFiltros() {
    const busqueda = normalizarTexto(inputBusqueda?.value || "");
    const estado = normalizarTexto(estadoSeleccionado);
    const tipo = normalizarTexto(tipoSeleccionado);

    let visibles = 0;

    filasReservas.forEach(fila => {
        const textoFila = normalizarTexto(fila.innerText);

        const cumpleBusqueda = textoFila.includes(busqueda);

        const cumpleEstado =
            estado === "todos los estados" ||
            textoFila.includes(estado);

        const cumpleTipo =
            tipo === "todos los tipos" ||
            textoFila.includes(tipo);

        if (cumpleBusqueda && cumpleEstado && cumpleTipo) {
            fila.style.display = "";
            visibles++;
        } else {
            fila.style.display = "none";
        }
    });

    if (btnFiltro) {
        btnFiltro.textContent = `☰ Filtros (${visibles})`;
    }
}

/* DROPDOWNS CUSTOM */

document.querySelectorAll(".custom-select").forEach(select => {
    const boton = select.querySelector(".custom-select-btn");
    const texto = select.querySelector(".custom-select-text");
    const opciones = select.querySelectorAll(".custom-options button");
    const filtro = select.dataset.filter;

    boton.addEventListener("click", event => {
        event.stopPropagation();

        document.querySelectorAll(".custom-select").forEach(item => {
            if (item !== select) {
                item.classList.remove("open");
            }
        });

        select.classList.toggle("open");
    });

    opciones.forEach(opcion => {
        opcion.addEventListener("click", event => {
            event.stopPropagation();

            const valor = opcion.dataset.value;
            texto.textContent = valor;

            if (filtro === "estado") {
                estadoSeleccionado = valor;
            }

            if (filtro === "tipo") {
                tipoSeleccionado = valor;
            }

            select.classList.remove("open");
            aplicarFiltros();
        });
    });
});

document.addEventListener("click", () => {
    document.querySelectorAll(".custom-select").forEach(select => {
        select.classList.remove("open");
    });
});
if (inputBusqueda) {
    inputBusqueda.addEventListener("input", aplicarFiltros);
}
if (btnFiltro) {
    btnFiltro.addEventListener("click", aplicarFiltros);
}

/* NUEVA RESERVA */
const modalNuevaReserva =
    document.getElementById("modalNuevaReserva");
const btnNuevaReserva =
    document.getElementById("btnNuevaReserva");
const btnCerrarNuevaReserva =
    document.getElementById("btnCerrarNuevaReserva");
const formNuevaReserva =
    document.getElementById("formNuevaReserva");
if (btnNuevaReserva) {
    btnNuevaReserva.addEventListener("click", () => {
        modalNuevaReserva.classList.add("show");
    });
}
if (btnCerrarNuevaReserva) {
    btnCerrarNuevaReserva.addEventListener("click", () => {
        modalNuevaReserva.classList.remove("show");
    });
}
const btnExportarReservas = document.getElementById("btnExportarReservas");

if (btnExportarReservas) {
    btnExportarReservas.addEventListener("click", () => {
        let csv = "Cliente,Correo,Fecha,Hora,Personas,Tipo,Estado\n";

        filasReservas.forEach(fila => {
            if (fila.style.display === "none") return;

            const columnas = fila.querySelectorAll("td");

            const cliente = columnas[0]?.innerText.replace(/\n/g, " ").trim();
            const fechaHora = columnas[1]?.innerText.replace(/\n/g, " ").trim();
            const personas = columnas[2]?.innerText.trim();
            const tipo = columnas[3]?.innerText.trim();
            const estado = columnas[4]?.innerText.trim();

            csv += `"${cliente}","${fechaHora}","${personas}","${tipo}","${estado}"\n`;
        });

        const blob = new Blob([csv], {
            type: "text/csv;charset=utf-8;"
        });

        const url = URL.createObjectURL(blob);

        const enlace = document.createElement("a");
        enlace.href = url;
        enlace.download = "reservas_cafeteria11.csv";
        enlace.click();

        URL.revokeObjectURL(url);

        alert("Reservas exportadas correctamente");
    });
}
if (window.flatpickr) {

    flatpickr("#fechaNuevaReserva", {
        dateFormat: "d/m/Y",
        minDate: "today"
    });

    flatpickr("#horaNuevaReserva", {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true
    });

}