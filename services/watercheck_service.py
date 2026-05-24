from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session
from models.schemas import Watercheck, EstandaresTDS
from services.email_service import send_watercheck_email

def process_water_quality(db: Session, watercheck: Watercheck):
    estandar = db.query(EstandaresTDS).filter(EstandaresTDS.id == watercheck.estandar_id).first()

    if not estandar:
        return

    if estandar.potable == 0 and watercheck.correo_enviado_hoy == 0:
        send_watercheck_email(db, watercheck.id, watercheck.id_ultima_medicion)
        watercheck.correo_enviado_hoy = 1
        
        
def get_estandar_id( db: Session, nivel_tds: float ):
    
    estandar = db.query(EstandaresTDS).filter( and_(
        EstandaresTDS.mayor_que <= nivel_tds,
        nivel_tds < EstandaresTDS.menor_que
    )).first()
    
    if not estandar:
        raise HTTPException(
            status_code=400,
            detail="El nivel TDS no corresponde a ningún estándar válido"
        )
    
    return estandar.id