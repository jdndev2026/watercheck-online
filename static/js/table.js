import { getStandardsData, getDataMediciones } from "./apis.js";
import { openDetail } from "./main.js";

export async function buildMainTable(puntos) {

	// obtenemos la parte del html donde se va a reenderizar la tabla
	const tbody = document.getElementById('mainTbody');

	// iniciamos un contador de puntos medidos
	let totalPuntos = 0;

	// recorremos los puntos
	puntos.forEach(p => {

		// Creamos el boton dentro del html
		tbody.innerHTML += `
			<tr>
				<td><strong>${p.id}</strong></td>
				<td>${p.total_mediciones}</td>
				<td>${p.ultima_fecha}</td>
				<td>${p.ultima_hora}</td>
				<td><span class="badge" style="color:${p.color};"><strong>${p.potabilidad}</strong></span></td>
				<td>
					<div class="actions-cell">
						<button class="btn btn-ver" data-id="${p.id}">Ver mediciones</button>
						<button class="btn btn-mail-active" watercheck-id="${p.id}" medicion-id="${p.id_ultima_medicion}" data-mail-enabled="true">Enviar correo</button>
					</div>
				</td>
			</tr>`;
		totalPuntos += 1;
	});

	document.querySelectorAll('.btn-ver').forEach(button => {
		button.addEventListener('click', () => {
			const puntoId = button.dataset.id;
			openDetail(puntoId);
		});
	});
}

function getFirstAndLastStandard( standardsData ){

	const firstStandard = standardsData.reduce((min, item) => {
		return item.mayor_que < min.mayor_que ? item : min;
	});

	const lastStandard = standardsData.reduce((min, item) => {
		return item.menor_que > min.menor_que ? item : min;
	});

	const filteredStandards = standardsData.filter(item => {
		return item.id !== firstStandard.id && item.id !== lastStandard.id;
	});

	return {firstStandard, lastStandard, filteredStandards};
}

export async function buildStandsrdsTable() {

	const standardsHtml = document.getElementById('standards-table');

	const standardsData = await getStandardsData();

	const {firstStandard, lastStandard, filteredStandards} = getFirstAndLastStandard( standardsData );

	// renderizamos el primer standar
	standardsHtml.innerHTML += `
		<div class="std-seg" style="background:${firstStandard.color}">
			${firstStandard.estandar}<span>(&lt;${firstStandard.menor_que})</span>
		</div>
	`;

	// renderizamos los demas standards
	filteredStandards.forEach( standard => {
		standardsHtml.innerHTML += `
			<div class="std-seg" style="background:${standard.color}">
				${standard.estandar}<span>(${standard.mayor_que}–${standard.menor_que})</span>
			</div>
		`;
	});


	// renderizamos el ultimo standar
	standardsHtml.innerHTML += `
		<div class="std-seg" style="background:${lastStandard.color}">
			${lastStandard.estandar}<span>(&gt;${lastStandard.mayor_que})</span>
		</div>
	`;
}

export async function buildDetailTable(puntoId) {

	document.getElementById('detailTitle').textContent = `Mediciones – ${puntoId}`;

	// Consumimos la api para obtener las mediciones
	const dataMediciones = await getDataMediciones( puntoId );

	// obtenemos el html donde se van a cargar los elementos
	const tbody = document.getElementById('detailTbody');

	dataMediciones.mediciones.forEach(m => {
	tbody.innerHTML += `
		<tr>
		<td><strong>${m.id_medicion}</strong></td>
		<td>${m.fecha}</td>
		<td>${m.hora}</td>
		<td>${m.tds}</td>
		<td>${m.turbidez}</td>
		<td>${m.ph}</td>
		<td><span class="badge" style="color:${m.color};"><strong>${m.potabilidad}</strong></span></td>
		<td>
			<button class="btn btn-mail-active" watercheck-id="${dataMediciones.id}" medicion-id="${m.id_medicion}" data-mail-enabled="true">Enviar correo</button>
		</td>
		</tr>`;
	});
}