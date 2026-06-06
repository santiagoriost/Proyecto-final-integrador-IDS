const reservas = JSON.parse(
    document.getElementById("reservas-json").textContent
);
const ventas = JSON.parse(
    document.getElementById("ventas-json").textContent
);
/* KPIs */
/* KPIs VENTAS */
const totalVentas = ventas.length;
const ingresosTotales = ventas.reduce(
    (total, venta) => total + parseFloat(venta.total || 0),
    0
);
document.getElementById("totalVentas").textContent =
    totalVentas;
document.getElementById("ingresosTotales").textContent =
    `$${ingresosTotales.toFixed(2)}`;
const total = reservas.length;

const confirmadas = reservas.filter(
    r => r.estado === "Confirmada"
).length;

const proceso = reservas.filter(
    r => r.estado === "En proceso"
).length;

const canceladas = reservas.filter(
    r => r.estado === "Cancelada"
).length;

document.getElementById("totalReservas").textContent = total;
/* GRÁFICO ESTADOS */
new Chart(
    document.getElementById("graficoEstados"),
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
                    labels: {
                        color: "#4B2E2B",
                        font: {
                            size: 13,
                            weight: "600"
                        }
                    }
                }
            },
            cutout: "68%"
        }
    }
);

/* TIPOS DE RESERVA */
const mesas = reservas.filter(r => r.tipo_reserva === "Mesa").length;
const productosReserva = reservas.filter(r => r.tipo_reserva === "Producto").length;

new Chart(
    document.getElementById("graficoTipos"),
    {
        type: "bar",
        data: {
            labels: ["Mesa", "Producto"],
            datasets: [{
                label: "Reservas",
                data: [mesas, productosReserva],
                backgroundColor: ["#E7B7A3", "#C8A27A"],
                borderRadius: 14
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#4B2E2B",
                        font: {
                            weight: "700"
                        }
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    ticks: {
                        color: "#4B2E2B"
                    },
                    grid: {
                        color: "rgba(75,46,43,0.10)"
                    }
                }
            }
        }
    }
);
/* VENTAS POR FECHA */
const ventasPorFecha = {};
ventas.forEach(venta => {
    const fecha = venta.fecha_venta
        ? venta.fecha_venta.substring(0, 10)
        : "Sin fecha";
    if (!ventasPorFecha[fecha]) {
        ventasPorFecha[fecha] = 0;
    }
    ventasPorFecha[fecha] += parseFloat(venta.total || 0);
});
new Chart(
    document.getElementById("graficoFechas"),
    {
        type: "line",
        data: {
            labels: Object.keys(ventasPorFecha),
            datasets: [{
                label: "Ingresos",
                data: Object.values(ventasPorFecha),
                borderColor: "#8B5E3C",
                backgroundColor: "rgba(231,183,163,0.35)",
                fill: true,
                tension: 0.4,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: "#4B2E2B",
                        font: {
                            weight: "700"
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: "#4B2E2B"
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    ticks: {
                        color: "#4B2E2B",
                        callback: value => "$" + value
                    },
                    grid: {
                        color: "rgba(75,46,43,0.10)"
                    }
                }
            }
        }
    }
);