from pydantic import BaseModel
from typing  import List

class EstandarTDSResponse(BaseModel):
    id        : int
    estandar  : str
    mayor_que : float
    menor_que : float
    potable   : int
    color     : str
    model_config = {
        "from_attributes": True
    }

class DataDashboardMainResponse(BaseModel):
    id: str
    estandar_id: int
    potabilidad: str
    total_mediciones: int
    ultima_fecha: str
    ultima_hora: str
    color: str
    potable: int
    correo_usuario: str
    id_ultima_medicion: int

class DataMedicionesByID(BaseModel):
    id_medicion: int
    fecha: str
    hora: str
    tds: float
    turbidez: float
    ph: float
    color: str
    potabilidad: str
    
class DataTableMediciones(BaseModel):
    id: str
    correo_usuario : str
    mediciones: List[DataMedicionesByID]