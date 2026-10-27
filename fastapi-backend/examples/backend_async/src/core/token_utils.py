# src\core\token_utils.py


from datetime import datetime, timezone, timedelta
from typing import Tuple
import uuid
from jose import jwt, JWTError

from .settings import settings


def create_token() -> str:
    """
    Genera un JWT firmado y con expiración.
    El 'sub' es un UUID aleatorio.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.TOKEN_SECONDS_EXP)

    data_token = {
        "sub": str(uuid.uuid4()),
        "exp": expires_at
        # (opcional) "iat": datetime.now(timezone.utc),
        # (opcional) "nbf": datetime.now(timezone.utc),
    }

    return jwt.encode(data_token, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> dict:
    """
    Verifica y decodifica un JWT. Lanza ValueError si es inválido o ha expirado.

    :param token: JWT a verificar
    :return: Payload del token si es válido
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Token inválido o expirado: {e}")
    
    
def get_uuid_and_exp_from_token(token: str) -> Tuple[str, datetime]:
    """
    Devuelve una tupla (uuid, exp) extraída del JWT.

    :param token: JWT a verificar
    :return: (uuid, exp) donde exp es un datetime timezone-aware en UTC
    """
    payload = verify_token(token)

    for field in ("sub", "exp"):
        if field not in payload:
            raise ValueError(f"El token no contiene el campo '{field}'")

    uuid_ = payload["sub"]
    exp_claim = payload["exp"]

    if isinstance(exp_claim, (int, float)):
        exp_dt = datetime.fromtimestamp(exp_claim, tz=timezone.utc)
    elif isinstance(exp_claim, datetime):
        exp_dt = exp_claim.astimezone(timezone.utc) if exp_claim.tzinfo else exp_claim.replace(tzinfo=timezone.utc)
    else:
        raise ValueError("Formato inesperado para el campo 'exp'")

    return uuid_, exp_dt