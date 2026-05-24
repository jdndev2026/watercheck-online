async function buildDonut(puntosValues, totalPuntos) {

	// Obtenemos los elementos del html necesarios
	const ctx = document.getElementById("donutChart").getContext("2d");

	new Chart(ctx, {
		type: "doughnut",
		data: {
			labels: puntosValues.map((punto) => punto.potabilidad),
			datasets: [
				{
					data: puntosValues.map((punto) => punto.cantidad),
					backgroundColor: puntosValues.map((punto) => punto.color),
					borderWidth: 2,
					borderColor: "#fff",
					hoverOffset: 6,
				},
			],
		},
		options: {
			cutout: "68%",
			plugins: {
				legend: { display: false },
				tooltip: {
					boxPadding: 6,
					callbacks: {
						label: (ctx) =>
							` ${ctx.label}: ${ctx.raw} lugares (${((ctx.raw / totalPuntos) * 100).toFixed(1)}%)`,
					},
				},
			},
			animation: { animateRotate: true, duration: 900 },
		},
	});

	// Porcentaje potable en el centro
	const potable = puntosValues.filter( punto => punto.potable > 0 ).reduce( (total, punto) => total+ punto.cantidad, 0);

	document.getElementById('donutPct').textContent =((potable / totalPuntos) * 100).toFixed(0) + '%';
}

// ─────────────────────────────────────────
// LEYENDA DEL GRÁFICO
// ─────────────────────────────────────────

async function buildLegend( puntosValues, totalPuntos ) {
	const legendHtml = document.getElementById("legendList");
	puntosValues.forEach((punto) => {

		const pct = ((punto.cantidad / totalPuntos) * 100).toFixed(1);
		legendHtml.innerHTML += `
			<div class="legend-item">
		<span class="legend-dot" style="background:${punto.color}"></span>
		<span class="legend-text">
				<span class="legend-count">${punto.potabilidad}</span> — ${punto.cantidad} lugares · ${pct}%
		</span>
			</div>`;
	});
}

export async function buildGraphic(dataMain) {
	// construimos el json con el conteo de puntos por estandar de calidad
	const jsonDataPuntos = {};

	dataMain.forEach((item) => {
		const id = item.estandar_id;

		if (!jsonDataPuntos[id]) {
			jsonDataPuntos[id] = {
				potabilidad: item.potabilidad,
				cantidad: 0,
				color: item.color,
				potable: item.potable
			};
		}

		jsonDataPuntos[id].cantidad++;
	});

	const puntosValues = Object.values(jsonDataPuntos);

	// Obtenemos el total de puntos medidos y lo enviamos a la seccion correspondiente
	const totalNumberId = document.getElementById('total-number');
	const totalPuntos = puntosValues.reduce( (total, item) => total + item.cantidad, 0 );
	totalNumberId.innerHTML += totalPuntos.toString();

	// llamamos las demas funciones del grafico
	await buildDonut(puntosValues, totalPuntos);
	await buildLegend(puntosValues, totalPuntos);
}
