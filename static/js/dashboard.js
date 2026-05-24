import { getDashboardMainData } from "./apis.js";
import { buildMainTable, buildStandsrdsTable } from "./table.js";
import { buildGraphic } from "./charts.js";

export async function loadDashboard() {

	try {

		const dataMain = await getDashboardMainData();

		await buildMainTable(dataMain);

		await buildGraphic(dataMain);

		await buildStandsrdsTable();

	} catch (error) {
		console.log('error: ', error);
	}

}