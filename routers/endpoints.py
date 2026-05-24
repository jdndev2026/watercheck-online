from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from datetime import datetime

from db.database import SessionLocal
from models.schemas import Watercheck, Mediciones, EstandaresTDS
from models.request_models import AddCheckRequest
from models.response_models import EstandarTDSResponse, DataDashboardMainResponse, DataMedicionesByID, DataTableMediciones
from services.watercheck_service import process_water_quality, get_estandar_id
from services.email_service import _get_email_data, build_email_html, send_email, build_asunto, send_watercheck_email

#########################################################################

def get_db():    
    db_connection = SessionLocal()   
    try:
        yield db_connection
    finally:
        db_connection.close()

#########################################################################

DB_DEPENDENCY = Annotated[ Session, Depends(get_db) ]

router = APIRouter()

@router.get("/standards-tds", response_model=List[EstandarTDSResponse])
async def get_standards_tds(db: DB_DEPENDENCY):
    standards = db.query(EstandaresTDS).all()
    return standards


@router.put("/upsert-watercheck", status_code=status.HTTP_200_OK)
async def upsert_mediciones( request: AddCheckRequest, db: DB_DEPENDENCY ):
    
    # definimos hora y fecha de insercion
    fecha_insert = datetime.now().strftime("%Y-%m-%d")
    hora_insert = datetime.now().strftime("%H:%M:%S")
    
    # validamos que la misma medicion no se haya hecho antes
    existing_mediciones = db.query(Mediciones).filter(
        Mediciones.watercheck_id == request.id,
        Mediciones.fecha         == fecha_insert,
        Mediciones.hora          == hora_insert
    ).first()
    
    # si se hizo antes, lanzamos excepcion
    if existing_mediciones: raise HTTPException( status_code=status.HTTP_409_CONFLICT, detail="Esta medicion ya existe")
    
    # obtenemos la informacion de los estandares de calidad
    estandar_id = get_estandar_id( db, request.tds )

    # insertamos el resgistro en la tabla mediciones
    medicion = Mediciones(
        watercheck_id = request.id,
        fecha         = fecha_insert,
        hora          = hora_insert,
        tds           = request.tds,
        turbidez      = request.turbidez,
        ph            = request.ph,
        estandar_id   = estandar_id
    )
    db.add(medicion)
    db.flush()
    
    # consultamos si el id que se desea insertar ya existe en la tabla watercheck
    watercheck = db.query(Watercheck).filter(Watercheck.id == request.id).first()
    
    # si no existe creamos el nuevo registro
    if not watercheck:
        watercheck = Watercheck(
            id                 = request.id,
            id_ultima_medicion = medicion.id,
            estandar_id        = estandar_id,
            correo_enviado_hoy = 0,
            correo_usuario     = request.correo_usuario
        )
        db.add(watercheck)
        db.flush()
    
    # si si existe, actualizamos id_ultima_medicion, estandar_id y correo de usuario
    else:
        watercheck.id_ultima_medicion = medicion.id
        watercheck.estandar_id        = estandar_id
        watercheck.correo_usuario     = request.correo_usuario
    
    # validamos si se debe enviar correo o no
    process_water_quality( db, watercheck )

    # confirmamos los cambios
    db.commit()

    return {
        "message": "Medicion guardada con exito"
    }
    

@router.get( "/data-dashboard-main", response_model=List[DataDashboardMainResponse] )
async def get_data_dashboard_main( db: DB_DEPENDENCY ):

    UltimaMedicion = aliased(Mediciones)

    resultados = (
        db.query(
            Watercheck.id                .label("id"),
            Watercheck.estandar_id       .label("estandar_id"),
            UltimaMedicion.fecha         .label("ultima_fecha"),
            UltimaMedicion.hora          .label("ultima_hora"),
            EstandaresTDS.estandar       .label("potabilidad"),
            EstandaresTDS.color          .label("color"),
            EstandaresTDS.potable        .label("potable"),
            func.count(Mediciones.id)    .label("total_mediciones"),
            Watercheck.correo_usuario    .label("correo_usuario"),
            Watercheck.id_ultima_medicion.label("id_ultima_medicion")
        )
        .join(EstandaresTDS,   Watercheck.estandar_id        == EstandaresTDS.id)
        .join(UltimaMedicion,  Watercheck.id_ultima_medicion == UltimaMedicion.id)
        .join(Mediciones,      Watercheck.id                 == Mediciones.watercheck_id)
        .group_by(Watercheck.id)
        .order_by(UltimaMedicion.fecha.desc(), UltimaMedicion.hora.desc())
        .all()
    )

    return [ DataDashboardMainResponse(**r._mapping) for r in resultados ]


@router.get( "/data-mediciones/{watercheck_id}", response_model=DataTableMediciones )
async def get_data_mediciones( db: DB_DEPENDENCY, watercheck_id: str ):
    
    # obtenemos el correo configurado para el usuario
    correo_usuario = db.query(Watercheck.correo_usuario).filter(Watercheck.id == watercheck_id).scalar()
    
    # Hacemos el query para extraer los datos necesarios
    mediciones = (
        db.query(
            Mediciones.id.label("id_medicion"),
            Mediciones.fecha.label("fecha"),
            Mediciones.hora.label("hora"),
            Mediciones.tds.label("tds"),
            Mediciones.turbidez.label("turbidez"),
            Mediciones.ph.label("ph"),
            EstandaresTDS.color.label("color"),
            EstandaresTDS.estandar.label("potabilidad")
        )
        .join(EstandaresTDS, Mediciones.estandar_id == EstandaresTDS.id)
        .filter(Mediciones.watercheck_id == watercheck_id)
        .order_by(Mediciones.fecha.desc(), Mediciones.hora.desc())
        .all()
    )

    data_mediciones = [ DataMedicionesByID(**m._mapping) for m in mediciones ]
    
    return {
        "id": watercheck_id,
        "correo_usuario": correo_usuario,
        "mediciones": data_mediciones
    }
    
    
@router.get("/preview-email/{watercheck_id}/{medicion_id}")
async def preview_email(watercheck_id: str, medicion_id: int, db: DB_DEPENDENCY):
    """
    Devuelve el HTML del correo renderizado para mostrarlo
    en la vista previa del modal antes de enviarlo.
    """
    try:
        data = _get_email_data(db, watercheck_id, medicion_id)
        html = build_email_html(data)
        return {
            "html"          : html,
            "asunto"        : build_asunto(data["watercheck_id"], data["potabilidad"], data["es_mala"]),
            "correo_usuario": data["correo_usuario"],
            "es_mala"       : data["es_mala"],
            "potabilidad"   : data["potabilidad"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/send-email/{watercheck_id}/{medicion_id}")
async def send_email_endpoint(watercheck_id: str, medicion_id: int, db: DB_DEPENDENCY):
    """
    Envía el correo manualmente desde el dashboard (botón del usuario).
    """
    try:
        send_watercheck_email(db, watercheck_id, medicion_id)
        return {"message": "Correo enviado con éxito"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar correo: {str(e)}")