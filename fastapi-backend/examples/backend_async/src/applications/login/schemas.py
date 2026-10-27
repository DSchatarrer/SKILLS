# backend\src\applications\login\schemas.py

from pydantic import BaseModel


class LoginRequest(BaseModel):
    usu: str
    pwd: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "usu": "your usu",
                "pwd": "your pwd"
            }
        }
    }
    
class LoginResponse(BaseModel):
    usu: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "usu": "your usu",
            }
        }
    }
    
    
class UserCreateRequest(BaseModel):
    usu: str
    pwd: str
    role: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "usu": "your usu",
                "pwd": "your pwd",
                "role": "admin"
            }
        }
    }

