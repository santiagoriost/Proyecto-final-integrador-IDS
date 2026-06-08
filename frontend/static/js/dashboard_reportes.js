const ventas   = JSON.parse(document.getElementById("ventas-json").textContent);
const reservas = JSON.parse(document.getElementById("reservas-json").textContent);

let graficoIngresos = null;
let graficoReservas = null;

/* Flatpickr */
flatpickr("#fechaDesde", { dateFormat: "Y-m-d", locale: "es" });
flatpickr("#fechaHasta", { dateFormat: "Y-m-d", locale: "es" });

document.getElementById("btnAplicarFiltro").addEventListener("click", aplicarFiltro);
document.getElementById("btnLimpiarFiltro").addEventListener("click", limpiarFiltro);
document.getElementById("btnExportarCSV").addEventListener("click", exportarCSV);

function aplicarFiltro() {
    const desde = document.getElementById("fechaDesde").value;
    const hasta = document.getElementById("fechaHasta").value;

    if (!desde || !hasta) {
        alert("Seleccioná ambas fechas");
        return;
    }

    const ventasFiltradas = ventas.filter(v => {
        if (!v.fecha_venta) return false;
        const fecha = v.fecha_venta.substring(0, 10);
        return fecha >= desde && fecha <= hasta;
    });

    const reservasFiltradas = reservas.filter(r => {
        if (!r.fecha_reserva) return false;
        return r.fecha_reserva >= desde && r.fecha_reserva <= hasta;
    });

    actualizarKPIs(ventasFiltradas, reservasFiltradas);
    actualizarGraficoIngresos(ventasFiltradas);
    actualizarGraficoReservas(reservasFiltradas);
    actualizarTabla(ventasFiltradas);
}

function limpiarFiltro() {
    document.getElementById("fechaDesde").value = "";
    document.getElementById("fechaHasta").value = "";
    document.getElementById("kpiIngresos").textContent   = "$0";
    document.getElementById("kpiVentas").textContent     = "0";
    document.getElementById("kpiReservas").textContent   = "0";
    document.getElementById("kpiPromedio").textContent   = "$0";
    document.getElementById("kpiIngresosDesc").textContent  = "—";
    document.getElementById("kpiVentasDesc").textContent    = "—";
    document.getElementById("kpiReservasDesc").textContent  = "—";
    document.getElementById("kpiPromedioDesc").textContent  = "—";
    document.getElementById("totalFilas").textContent = "0 registros";
    document.getElementById("tablaVentasBody").innerHTML =
        `<tr><td colspan="4" class="sin-datos">Seleccioná un período para ver los datos</td></tr>`;
    if (graficoIngresos) { graficoIngresos.destroy(); graficoIngresos = null; }
    if (graficoReservas) { graficoReservas.destroy(); graficoReservas = null; }
}

function actualizarKPIs(ventasFiltradas, reservasFiltradas) {
    const ingresos = ventasFiltradas.reduce((t, v) => t + parseFloat(v.total || 0), 0);
    const promedio = ventasFiltradas.length ? ingresos / ventasFiltradas.length : 0;
    const confirmadas = reservasFiltradas.filter(r => r.estado === "Confirmada").length;
    const canceladas  = reservasFiltradas.filter(r => r.estado === "Cancelada").length;

    document.getElementById("kpiIngresos").textContent  = `$${ingresos.toFixed(2)}`;
    document.getElementById("kpiVentas").textContent    = ventasFiltradas.length;
    document.getElementById("kpiReservas").textContent  = reservasFiltradas.length;
    document.getElementById("kpiPromedio").textContent  = `$${promedio.toFixed(2)}`;
    document.getElementById("kpiIngresosDesc").textContent  = `${ventasFiltradas.length} transacciones`;
    document.getElementById("kpiVentasDesc").textContent    = `en el período seleccionado`;
    document.getElementById("kpiReservasDesc").textContent  = `${confirmadas} confirmadas · ${canceladas} canceladas`;
    document.getElementById("kpiPromedioDesc").textContent  = `por venta`;
}

function actualizarGraficoIngresos(ventasFiltradas) {
    const porFecha = {};
    ventasFiltradas.forEach(v => {
        const fecha = v.fecha_venta ? v.fecha_venta.substring(0, 10) : "Sin fecha";
        porFecha[fecha] = (porFecha[fecha] || 0) + parseFloat(v.total || 0);
    });

    if (graficoIngresos) graficoIngresos.destroy();

    graficoIngresos = new Chart(
        document.getElementById("graficoIngresosPeriodo"),
        {
            type: "line",
            data: {
                labels: Object.keys(porFecha),
                datasets: [{
                    label: "Ingresos",
                    data: Object.values(porFecha),
                    borderColor: "#8B5E3C",
                    backgroundColor: "rgba(231,183,163,0.35)",
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { labels: { color: "#4B2E2B", font: { weight: "700" } } } },
                scales: {
                    x: { ticks: { color: "#4B2E2B" }, grid: { display: false } },
                    y: {
                        ticks: { color: "#4B2E2B", callback: v => "$" + v },
                        grid: { color: "rgba(75,46,43,0.10)" }
                    }
                }
            }
        }
    );
}

function actualizarGraficoReservas(reservasFiltradas) {
    const confirmadas = reservasFiltradas.filter(r => r.estado === "Confirmada").length;
    const proceso     = reservasFiltradas.filter(r => r.estado === "En proceso").length;
    const canceladas  = reservasFiltradas.filter(r => r.estado === "Cancelada").length;

    if (graficoReservas) graficoReservas.destroy();

    graficoReservas = new Chart(
        document.getElementById("graficoReservasPeriodo"),
        {
            type: "doughnut",
            data: {
                labels: ["Confirmadas", "En proceso", "Canceladas"],
                datasets: [{
                    data: [confirmadas, proceso, canceladas],
                    backgroundColor: ["#C8A27A", "#E7B7A3", "#8B5E3C"],
                    borderWidth: 0,
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#4B2E2B", font: { size: 13, weight: "600" } }
                    }
                },
                cutout: "68%"
            }
        }
    );
}

function actualizarTabla(ventasFiltradas) {
    const tbody = document.getElementById("tablaVentasBody");
    document.getElementById("totalFilas").textContent = `${ventasFiltradas.length} registros`;

    if (!ventasFiltradas.length) {
        tbody.innerHTML = `<tr><td colspan="4" class="sin-datos">Sin ventas en este período</td></tr>`;
        return;
    }

    tbody.innerHTML = ventasFiltradas.map(v => `
        <tr>
            <td>${v.fecha_venta ? v.fecha_venta.substring(0, 10) : "—"}</td>
            <td>${v.nombre_producto || "—"}</td>
            <td>${v.cantidad || "—"}</td>
            <td>$${parseFloat(v.total || 0).toFixed(2)}</td>
        </tr>
    `).join("");
}

function exportarCSV() {
    const desde = document.getElementById("fechaDesde").value;
    const hasta = document.getElementById("fechaHasta").value;
    const ventasFiltradas = ventas.filter(v => {
        if (!v.fecha_venta) return false;
        const fecha = v.fecha_venta.substring(0, 10);
        return (!desde || fecha >= desde) && (!hasta || fecha <= hasta);
    });

    if (!ventasFiltradas.length) { alert("No hay datos para exportar"); return; }

    const filas = [
        ["Fecha", "Producto", "Cantidad", "Total"],
        ...ventasFiltradas.map(v => [
            v.fecha_venta ? v.fecha_venta.substring(0, 10) : "—",
            v.nombre_producto || "—",
            v.cantidad || "—",
            parseFloat(v.total || 0).toFixed(2)
        ])
    ];

    const csv = filas.map(f => f.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href     = url;
    a.download = `reporte_${desde}_${hasta}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}