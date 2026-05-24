import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session
from datetime import datetime

from models.schemas import Watercheck, Mediciones, EstandaresTDS


load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def _get_email_data(db: Session, watercheck_id: str, medicion_id: int) -> dict:
    """
    Consulta en la BD todos los datos necesarios para construir el correo,
    usando watercheck_id y medicion_id como punto de entrada.
    Retorna un dict listo para pasarle al template Jinja2.
    """
    medicion = (
        db.query(
            Mediciones.id       .label("medicion_id"),
            Mediciones.fecha    .label("fecha"),
            Mediciones.hora     .label("hora"),
            Mediciones.tds      .label("tds"),
            Mediciones.turbidez .label("turbidez"),
            Mediciones.ph       .label("ph"),
            EstandaresTDS.estandar .label("potabilidad"),
            EstandaresTDS.color    .label("color"),
            EstandaresTDS.potable  .label("potable"),
        )
        .join(EstandaresTDS, Mediciones.estandar_id == EstandaresTDS.id)
        .filter(Mediciones.id == medicion_id)
        .first()
    )

    if not medicion:
        raise ValueError(f"No se encontró la medición con id {medicion_id}")

    correo_usuario = (
        db.query(Watercheck.correo_usuario)
        .filter(Watercheck.id == watercheck_id)
        .scalar()
    )

    es_mala = medicion.potable < 1

    return {
        "watercheck_id" : watercheck_id,
        "medicion_id"   : medicion.medicion_id,
        "fecha"         : medicion.fecha,
        "hora"          : medicion.hora,
        "tds"           : medicion.tds,
        "turbidez"      : medicion.turbidez,
        "ph"            : medicion.ph,
        "potabilidad"   : medicion.potabilidad,
        "color"         : medicion.color,
        "es_mala"       : es_mala,
        "correo_usuario": correo_usuario,
        "anio"          : datetime.now().year
    }


def build_email_html(data: dict) -> str:
    """
    Renderiza el template Jinja2 con los datos del correo.
    Úsala tanto para la vista previa (endpoint GET) como para el envío.
    """
    env      = Environment(loader=FileSystemLoader("static"))
    template = env.get_template("email_template.html")
    return template.render(**data)


def send_email(html: str, asunto: str, destinatario: str):
    """Envía el correo por SMTP."""
    msg            = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = SMTP_USER
    msg["To"]      = destinatario
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())


def build_asunto(watercheck_id: str, potabilidad: str, es_mala: bool) -> str:
    if es_mala:
        return f"ALERTA: Punto {watercheck_id} – calidad {potabilidad} – Watercheck Online"
    return f"Reporte de potabilidad – {watercheck_id} – Watercheck Online"


def send_watercheck_email(db: Session, watercheck_id: str, medicion_id: int):
    """
    Función de alto nivel que hace todo: consulta, renderiza y envía.
    Llámala desde watercheck_service.py cuando detectes mala calidad.
    """
    data      = _get_email_data(db, watercheck_id, medicion_id)
    html      = build_email_html(data)
    asunto    = build_asunto(data["watercheck_id"], data["potabilidad"], data["es_mala"])
    send_email(html, asunto, data["correo_usuario"])