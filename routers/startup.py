
from db.database import SessionLocal
from models.schemas import EstandaresTDS

async def startup_database():
    db = SessionLocal()
    
    try:    
        db_existente = db.query(EstandaresTDS).first()

        if not db_existente:
            
            initial_data = [
                EstandaresTDS(
                    estandar="Excelente",
                    mayor_que=0,
                    menor_que=300,
                    potable=1,
                    color="#009fff"
                ),
                EstandaresTDS(
                    estandar="Buena",
                    mayor_que=300,
                    menor_que=600,
                    potable=1,
                    color="#22c55e"
                ),
                EstandaresTDS(
                    estandar="Regular",
                    mayor_que=600,
                    menor_que=900,
                    potable=0,
                    color="#facc15"
                ),
                EstandaresTDS(
                    estandar="Pobre",
                    mayor_que=900,
                    menor_que=1200,
                    potable=0,
                    color="#f97316"
                ),
                EstandaresTDS(
                    estandar="Inaceptable",
                    mayor_que=1200,
                    menor_que=9999,
                    potable=0,
                    color="#ef4444"
                )
            ]
            
            db.add_all( initial_data )
            db.commit()
    
    finally:
        db.close()