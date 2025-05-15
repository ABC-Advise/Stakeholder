from fastapi import HTTPException
from typing import Any, Dict, Optional

class APIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

def handle_api_error(error: APIError) -> HTTPException:
    """
    Converte um APIError em uma HTTPException do FastAPI
    """
    return HTTPException(
        status_code=error.status_code,
        detail={
            "message": error.message,
            "details": error.details
        }
    )

class ProfileNotFoundError(APIError):
    def __init__(self, username: str):
        super().__init__(
            message=f"Perfil não encontrado: {username}",
            status_code=404,
            details={"username": username}
        )

class HikerAPIError(APIError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Erro na Hiker API: {message}",
            status_code=502,
            details=details
        )

class DatabaseError(APIError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Erro no banco de dados: {message}",
            status_code=500,
            details=details
        ) 