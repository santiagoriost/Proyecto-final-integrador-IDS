const reservas = JSON.parse(
    document.getElementById("reservas-json").textContent
);
const ventas = JSON.parse(
    document.getElementById("ventas-json").textContent
);
const masVendidos = JSON.parse(
    document.getElementById("mas-vendidos-json").textContent
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
const productoEstrella = masVendidos.length > 0
    ? masVendidos[0].nombre_producto || masVendidos[0].nombre || "---"
    : "---";

document.getElementById("productoEstrella").textContent = productoEstrella;

const total = reservas.length;
document.getElementById("totalReservas").textContent = total;

/* FUNCIONES AUXILIARES */
function obtenerFecha(valorFecha) {
    if (!valorFecha) {
        return "Sin fecha";
    }

    return String(valorFecha).substring(0, 10);
}

function agruparConteoPorFecha(lista, campoFecha) {
    const datosPorFecha = {};

    lista.forEach(item => {
        const fecha = obtenerFecha(item[campoFecha]);

        if (!datosPorFecha[fecha]) {
            datosPorFecha[fecha] = 0;
        }

        datosPorFecha[fecha] += 1;
    });

    return datosPorFecha;
}

/* VENTAS POR FECHA - CANTIDAD */
const cantidadVentasPorFecha = agruparConteoPorFecha(
    ventas,
    "fecha_venta"
);

new Chart(
    document.getElementById("graficoVentasFecha"),
    {
        type: "bar",
        data: {
            labels: Object.keys(cantidadVentasPorFecha),
            datasets: [{
                label: "Ventas",
                data: Object.values(cantidadVentasPorFecha),
                backgroundColor: "rgba(111, 44, 145, 0.45)",
                borderColor: "#6F2C91",
                borderWidth: 2,
                borderRadius: 14
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
                            weight: "700"
                        }
                    }
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
                    beginAtZero: true,
                    ticks: {
                        color: "#4B2E2B",
                        precision: 0
                    },
                    grid: {
                        color: "rgba(75,46,43,0.10)"
                    }
                }
            }
        }
    }
);

/* RESERVAS POR FECHA */
const reservasPorFecha = agruparConteoPorFecha(
    reservas,
    "fecha_reserva"
);

new Chart(
    document.getElementById("graficoReservasFecha"),
    {
        type: "line",
        data: {
            labels: Object.keys(reservasPorFecha),
            datasets: [{
                label: "Reservas",
                data: Object.values(reservasPorFecha),
                borderColor: "#E0A100",
                backgroundColor: "rgba(234, 232, 75, 0.25)",
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7
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
                            weight: "700"
                        }
                    }
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
                    beginAtZero: true,
                    ticks: {
                        color: "#4B2E2B",
                        precision: 0
                    },
                    grid: {
                        color: "rgba(75,46,43,0.10)"
                    }
                }
            }
        }
    }
);

/* INGRESOS POR FECHA */
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