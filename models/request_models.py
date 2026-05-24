from pydantic import BaseModel, Field

class AddCheckRequest(BaseModel):
    
    id             : str = Field( min_length=1, max_length=10 )
    tds            : float
    turbidez       : float
    ph             : float
    correo_usuario : str = Field( max_length=200 )
    
    model_config = {
        "json_schema_extra" : {
            "example" : {
                "id": "11111",
                "tds" : 345,
                "turbidez": 456,
                "ph" : 567,
                "correo_usuario": "prueba@gmail.com"
            }
        }
    }
    