import os
import json
from pathlib import Path
from dotenv import load_dotenv

from db.database import SessionLocal
from models.schemas import EstandaresTDS, Watercheck, Mediciones
from services.watercheck_service import get_estandar_id

load_dotenv()

async def startup_estandars():
    
    db = SessionLocal()
    
    try:
        # Obtenemos el path de la variable de entorno
        standards_path_env = os.getenv("STANDARDS_JSON_PATH")
        
        # Validamos si existen registros dentro de la tabla
        estandares_existentes = db.query(EstandaresTDS).first()

        # Si no hay registros los insertamos
        if not estandares_existentes:            
            standars_file = Path(standards_path_env)         
            
            # Si no existe el json con la data no hacemos insercion
            if standars_file.exists():
                
                # Leemos el archivo y almacenamos el json
                with open(standars_file, encoding="utf-8") as myfile:
                    standards_json = json.load(myfile)
                        
                # Cargamos la data usando lista por comprension
                db.add_all([ EstandaresTDS(**row) for row in standards_json ])

                # Hacemos commit ya que esta data es independiente del resto del proceso y debe existir siempre
                db.commit()
    
    finally:
        db.close()


async def startup_data():
    
    db = SessionLocal()
    
    try:
        # Obtenemos el path de la variable de entorno
        seed_data_path_env = os.getenv("SEED_DATA_PATH")
        
        # Validamos si hay registros en la base de datos de watercheck
        waterchecks_existentes = db.query(Watercheck).first()
        
        # Validamos si existe la variable de entorno con el path a la data de prueba, en produccion no debe existir ya que es solo para desarrollo y demostracion
        if not waterchecks_existentes and seed_data_path_env:
            seed_data_file = Path(seed_data_path_env)         
            
            # Si no existe el json con la data no hacemos insercion
            if seed_data_file.exists():
                
                # Leemos el archivo y almacenamos el json
                with open(seed_data_file, encoding="utf-8") as myfile:
                    seed_data_json = json.load(myfile)
                
                # Insertamos los registros de watercheck
                db.add_all([ Watercheck(**row) for row in seed_data_json.get("watercheck", []) ])
                db.flush()
                
                # Obtenemos los registros de mediciones en de mas antiguo a mas reciente
                json_mediciones = sorted(
                    seed_data_json.get("mediciones", []),
                    key=lambda x: (x["fecha"], x["hora"])
                )
                
                # Insertamos cada registro
                for row in json_mediciones:

                    estandar_id = get_estandar_id( db, row["tds"] )

                    medicion = Mediciones(
                        watercheck_id = row["watercheck_id"],
                        fecha         = row["fecha"],
                        hora          = row["hora"],
                        tds           = row["tds"],
                        turbidez      = row["turbidez"],
                        ph            = row["ph"],
                        estandar_id   = estandar_id
                    )

                    db.add(medicion)
                    db.flush()
                    
                    # Actualizamos el id_ultima_medicion y estandar_id del registro recien agregado
                    watercheck = db.query(Watercheck).filter(Watercheck.id == row["watercheck_id"]).first()

                    watercheck.id_ultima_medicion = medicion.id
                    watercheck.estandar_id = estandar_id
                
                # Confirmamos el commit
                db.commit()
    
    finally:
        db.close()