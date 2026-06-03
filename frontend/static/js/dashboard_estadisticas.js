async function cargarEstadisticas() {
    try {
        const respuesta = await fetch(
            "http://127.0.0.1:5001/reservas/?limit=100"
        );
        const datos = await respuesta.json();
        const reservas = datos.reservas || [];

// KPIs
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
        document.getElementById("reservasConfirmadas").textContent =
            confirmadas;
        document.getElementById("reservasProceso").textContent =
            proceso;
        document.getElementById("reservasCanceladas").textContent =
            canceladas;

//GRÁFICO ESTADOS 

        new Chart(
            document.getElementById("graficoEstados"),
            {
                type: "doughnut",
                data: {
                    labels: [
                        "Confirmadas",
                        "En proceso",
                        "Canceladas"
                    ],
                    datasets: [{
                        data: [
                            confirmadas,
                            proceso,
                            canceladas
                        ]
                    }]
                }
            }
        );

// TIPOS 
        const mesas = reservas.filter(
            r => r.tipo_reserva === "Mesa"
        ).length;
        const productos = reservas.filter(
            r => r.tipo_reserva === "Producto"
        ).length;
        new Chart(
            document.getElementById("graficoTipos"),
            {
                type: "bar",
                data: {
                    labels: [
                        "Mesa",
                        "Producto"
                    ],
                    datasets: [{
                        label: "Reservas",
                        data: [
                            mesas,
                            productos
                        ]
                    }]
                }
            }
        );
//FECHAS 
        const reservasPorFecha = {};
        reservas.forEach(reserva => {
            const fecha = reserva.fecha_reserva;
            if (!reservasPorFecha[fecha]) {
                reservasPorFecha[fecha] = 0;
            }
            reservasPorFecha[fecha]++;
        });
        new Chart(
            document.getElementById("graficoFechas"),
            {
                type: "line",
                data: {
                    labels: Object.keys(reservasPorFecha),
                    datasets: [{
                        label: "Reservas",
                        data: Object.values(reservasPorFecha)
                    }]
                }
            }
        );
    } catch (error) {
        console.error(error);
    }
}
cargarEstadisticas();