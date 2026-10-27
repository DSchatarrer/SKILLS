# backend\src\applications\pacientes\schemas.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class PacienteNombreItem(BaseModel):
    id: int
    username: str


class PacienteNombresResponseModel(BaseModel):
    nombres: List[PacienteNombreItem]

    model_config = {
        "json_schema_extra": {
            "example": {
                "nombres": [
                    {"id": 1, "username": "juanperez"},
                    {"id": 2, "username": "mariagonzalez"},
                    {"id": 3, "username": "carlossanchez"}
                ]
            }
        }
    }


class PacienteCreateModel(BaseModel):
    username: str


class PacienteUpdateModel(BaseModel):
    username: Optional[str] = None


class PacienteResponseModel(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }




