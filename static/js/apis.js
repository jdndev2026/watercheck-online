const API_BASE_URL = window.location.origin;

export async function getDashboardMainData() {
	const response = await fetch(
		`${API_BASE_URL}/data-dashboard-main`
	);
	if (!response.ok) {
		throw new Error("Error obteniendo dashboard");
	}
	return await response.json();
}


export async function getStandardsData(){
	const response = await fetch(
		`${API_BASE_URL}/standards-tds`
	);
	if (!response.ok) {
		throw new Error("Error obteniendo Data Standards");
	}
	return await response.json();
}


export async function getDataMediciones( watercheckID ) {
	const response = await fetch(
		`${API_BASE_URL}/data-mediciones/${watercheckID}`
	);
	if (!response.ok) {
		throw new Error(`Error obteniendo mediciones id ${watercheckID}`);
	}
	return await response.json();
}


export async function getEmailPreview(watCheckId, medicionId) {
    const response = await fetch(
        `${API_BASE_URL}/preview-email/${watCheckId}/${medicionId}`
    );
    if (!response.ok) throw new Error("Error obteniendo vista previa del correo");
    return await response.json();
}


export async function sendEmail(watCheckId, medicionId) {
    const response = await fetch(
        `${API_BASE_URL}/send-email/${watCheckId}/${medicionId}`,
        { method: "POST" }
    );
    if (!response.ok) throw new Error("Error enviando correo");
    return await response.json();
}