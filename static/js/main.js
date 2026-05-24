import { loadDashboard } from "./dashboard.js";
import { buildDetailTable } from "./table.js";
import { getEmailPreview, sendEmail } from "./apis.js";

// reenderiza la pagina principal
window.addEventListener("DOMContentLoaded", async () => {

	// espera que todos los elementos carguen
	await loadDashboard();

	// insertamos funciones en elementos no dinamicos
	document.querySelector('.back-btn').addEventListener('click', goBack);
	document.getElementById('modalCloseBtn').addEventListener('click', closeModal);
	document.getElementById('modalCancelBtn').addEventListener('click', closeModal);
});

// funcion para abrir la tabla de mediciones de cada id
export function openDetail(puntoId){
	buildDetailTable(puntoId);
	document.getElementById('page1').classList.remove('active');
	document.getElementById('page2').classList.add('active');
	window.scrollTo(0, 0);
}

// al regresar, se recarga la pagina para que siempre se actualice
export function goBack(){ window.location.reload(); }


// ── Modal de correo ──────────────────────────────────────

function openModal(previewData) {
    const modal = document.getElementById('emailModal');
    const head  = document.getElementById('modalHead');
    const title = document.getElementById('modalTitle');
    const subj  = document.getElementById('emailSubject');
    const body  = document.getElementById('emailContent');

	document.getElementById('emailDestinatario').textContent = previewData.correo_usuario;

    head.className    = `modal-head ${previewData.es_mala ? 'alert' : 'info'}`;
    title.textContent = previewData.es_mala ? '⚠️ Alerta de Potabilidad' : '📋 Reporte de Potabilidad';
    subj.textContent  = previewData.asunto;
    body.innerHTML    = previewData.html;

    modal.classList.add('open');
}

export function closeModal() {
    document.getElementById('emailModal').classList.remove('open');
}

// Cierra el modal al hacer click fuera
document.getElementById('emailModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
});

// Delegación de eventos para botones de correo generados dinámicamente
document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-mail-enabled="true"]');
    if (!btn) return;

    const watCheckId = btn.getAttribute('watercheck-id');
    const medicionId = btn.getAttribute('medicion-id');

    try {
        // Carga la vista previa desde la BD y abre el modal
        const previewData = await getEmailPreview(watCheckId, medicionId);
        openModal(previewData);

        // Registra el botón "Enviar correo" del modal para este correo concreto
        const sendBtn = document.querySelector('.btn-send');
        // Clona el botón para limpiar listeners previos
        const newSendBtn = sendBtn.cloneNode(true);
        sendBtn.parentNode.replaceChild(newSendBtn, sendBtn);

		newSendBtn.addEventListener('click', async () => {
			closeModal();
			Swal.fire({
				title             : 'Enviando correo...',
				text              : 'Por favor espera.',
				allowOutsideClick : false,
				allowEscapeKey    : false,
				showConfirmButton : false,
				didOpen           : () => Swal.showLoading()
			});
			try {
				await sendEmail(watCheckId, medicionId);
				Swal.fire({
					icon : 'success',
					title: '¡Correo enviado!',
					text : 'El correo fue enviado correctamente.',
					confirmButtonColor: '#2563a8'
				});
			} catch (err) {
				console.error(err);
				Swal.fire({
					icon : 'error',
					title: 'Error al enviar',
					text : 'No se pudo enviar el correo. Intenta nuevamente.',
					confirmButtonColor: '#ef4444'
				});
			}
		});

    } catch (err) {
        console.error('Error cargando vista previa:', err);
        alert('No se pudo cargar la vista previa del correo');
    }
});