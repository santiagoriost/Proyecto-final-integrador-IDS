const productoVenta = document.getElementById("productoVenta");
const cantidadVenta = document.getElementById("cantidadVenta");
const totalVenta = document.getElementById("totalVenta");
const customSelect = document.querySelector(".ventas-product-select");
const customBtn = customSelect.querySelector(".custom-select-btn");
const customText = customSelect.querySelector(".custom-select-text");
const customOptions = customSelect.querySelectorAll(".custom-options button");
const toastVenta = document.getElementById("toastVenta");
function mostrarToast(
    mensaje,
    tipo = "success"
){
    toastVenta.textContent = mensaje;
    toastVenta.className =
        `toast-venta show ${tipo}`;
    setTimeout(() => {
        toastVenta.classList.remove("show");
    }, 2500);
}
function actualizarTotal(){
    const productoSeleccionado = document.querySelector(
        `.custom-options button[data-value="${productoVenta.value}"]`
    );
    if(!productoSeleccionado){
        totalVenta.textContent = "0.00";
        return;
    }
    const precio = parseFloat(productoSeleccionado.dataset.precio);
    const cantidad = parseInt(cantidadVenta.value || 0);

    totalVenta.textContent = (precio * cantidad).toFixed(2);
}

customBtn.addEventListener("click", () => {
    customSelect.classList.toggle("active");
});

customOptions.forEach(option => {
    option.addEventListener("click", () => {
        productoVenta.value = option.dataset.value;
        customText.textContent = option.textContent;
        customSelect.classList.remove("active");
        actualizarTotal();
    });
});

document.addEventListener("click", (e) => {
    if(!customSelect.contains(e.target)){
        customSelect.classList.remove("active");
    }
});

cantidadVenta.addEventListener("input", actualizarTotal);
formVenta.addEventListener("submit", (event) => {
    if(!productoVenta.value || !cantidadVenta.value){
        event.preventDefault();
        mostrarToast(
            "selecciona un producto y cantidad",
            "error"
        );
        return;
    }
});

const filtroFechaDesde = document.getElementById("filtroFechaDesde");
const filtroFechaHasta = document.getElementById("filtroFechaHasta");
const filtroTotalMin = document.getElementById("filtroTotalMin");
const filtroTotalMax = document.getElementById("filtroTotalMax");
const btnLimpiarFiltrosVentas = document.getElementById("btnLimpiarFiltrosVentas");

function filtrarVentas(){
    const filas = document.querySelectorAll("tbody tr");

    filas.forEach(fila => {
        const fechaTexto = fila.children[1].textContent.trim();
        const totalTexto = fila.children[2].textContent.replace("$", "").trim();

        const total = parseFloat(totalTexto);
        const fechaVenta = new Date(fechaTexto);

        const desde = filtroFechaDesde.value ? new Date(filtroFechaDesde.value) : null;
        const hasta = filtroFechaHasta.value ? new Date(filtroFechaHasta.value) : null;

        const totalMin = filtroTotalMin.value ? parseFloat(filtroTotalMin.value) : null;
        const totalMax = filtroTotalMax.value ? parseFloat(filtroTotalMax.value) : null;

        let visible = true;

        if(desde && fechaVenta < desde) visible = false;
        if(hasta && fechaVenta > hasta) visible = false;
        if(totalMin !== null && total < totalMin) visible = false;
        if(totalMax !== null && total > totalMax) visible = false;

        fila.style.display = visible ? "" : "none";
    });
}

filtroFechaDesde.addEventListener("input", filtrarVentas);
filtroFechaHasta.addEventListener("input", filtrarVentas);
filtroTotalMin.addEventListener("input", filtrarVentas);
filtroTotalMax.addEventListener("input", filtrarVentas);

btnLimpiarFiltrosVentas.addEventListener("click", () => {
    filtroFechaDesde.value = "";
    filtroFechaHasta.value = "";
    filtroTotalMin.value = "";
    filtroTotalMax.value = "";

    filtrarVentas();
});

if (window.flatpickr) {
    flatpickr("#filtroFechaDesde", {
        dateFormat: "Y-m-d",
        monthSelectorType: "static"
    });

    flatpickr("#filtroFechaHasta", {
        dateFormat: "Y-m-d",
        monthSelectorType: "static"
    });
}
const modalDetalle = document.getElementById("modalDetalleVenta");
const cerrarModal = document.getElementById("cerrarModalDetalle");
const contenidoDetalle = document.getElementById("contenidoDetalleVenta");

document.querySelectorAll(".btn-detalle-venta").forEach(boton => {
    boton.addEventListener("click", () => {
        const idVenta = boton.dataset.id;
        const contenedorDatos = document.querySelector(
            `.detalle-venta-data[data-id="${idVenta}"]`
        );
        modalDetalle.style.display = "flex";
        if (!contenedorDatos) {
            contenidoDetalle.innerHTML = "No se encontraron detalles para esta venta.";
            return;
        }
        const items = contenedorDatos.querySelectorAll(".detalle-item");
        let html = `
            <div class="modal-venta-header">
                <strong>Venta #${idVenta}</strong>
            </div>
        `;
        items.forEach(item => {
            html += `
                <div class="detalle-producto-modal">
                    <strong>${item.dataset.nombre}</strong>
                    <p>Cantidad: ${item.dataset.cantidad}</p>
                    <p>Precio unitario: $${item.dataset.precio}</p>
                    <p>Subtotal: $${item.dataset.subtotal}</p>
                </div>
            `;
        });
        contenidoDetalle.innerHTML = html;
    });
});
cerrarModal.addEventListener("click", () => {
    modalDetalle.style.display = "none";
});
window.addEventListener("click", (e) => {
    if (e.target === modalDetalle) {
        modalDetalle.style.display = "none";
    }
});