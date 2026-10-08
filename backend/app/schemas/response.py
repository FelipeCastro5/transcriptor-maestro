from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class ResponseDto(BaseModel, Generic[DataT]):
    """
    DTO Estándar de Respuesta para toda la API.
    Estructura unificada idéntica a response.util.ts:
      - code: Código numérico de estado HTTP
      - message: Mensaje descriptivo para el cliente/frontend
      - data: Carga útil serializada o null
    """
    code: int = Field(..., description="Código de estado HTTP")
    message: str = Field(..., description="Mensaje informativo o de error")
    data: Optional[DataT] = Field(None, description="Carga de datos o null")

    class Config:
        populate_by_name = True

class ResponseUtil:
    """
    Utilidad para instanciar respuestas estandarizadas ResponseDto en Python.
    Equivalente exacto a la clase ResponseUtil en TypeScript.
    """
    @staticmethod
    def custom(code: int, message: str, data: Any = None) -> ResponseDto:
        return ResponseDto(code=code, message=message, data=data)

    @staticmethod
    def success(data: Any, message: str = "Operación exitosa", code: int = 200) -> ResponseDto:
        return ResponseDto(code=code, message=message, data=data)

    @staticmethod
    def created(data: Any, message: str = "Recurso creado") -> ResponseDto:
        return ResponseDto(code=201, message=message, data=data)

    @staticmethod
    def accepted(data: Any, message: str = "Solicitud aceptada") -> ResponseDto:
        return ResponseDto(code=202, message=message, data=data)

    @staticmethod
    def no_content(message: str = "Sin contenido") -> ResponseDto:
        return ResponseDto(code=204, message=message, data=None)

    @staticmethod
    def bad_request(message: str = "Solicitud inválida") -> ResponseDto:
        return ResponseDto(code=400, message=message, data=None)

    @staticmethod
    def unauthorized(message: str = "Token inválido o faltante") -> ResponseDto:
        return ResponseDto(code=401, message=message, data=None)

    @staticmethod
    def forbidden(message: str = "Acceso denegado") -> ResponseDto:
        return ResponseDto(code=403, message=message, data=None)

    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> ResponseDto:
        return ResponseDto(code=404, message=message, data=None)

    @staticmethod
    def conflict(message: str = "Conflicto en la solicitud") -> ResponseDto:
        return ResponseDto(code=409, message=message, data=None)

    @staticmethod
    def unprocessable(message: str = "Entidad no procesable") -> ResponseDto:
        return ResponseDto(code=422, message=message, data=None)

    @staticmethod
    def internal(message: str = "Error interno del servidor") -> ResponseDto:
        return ResponseDto(code=500, message=message, data=None)

    @staticmethod
    def service_unavailable(message: str = "Servicio no disponible") -> ResponseDto:
        return ResponseDto(code=503, message=message, data=None)

    @staticmethod
    def error(message: str, code: int = 400) -> ResponseDto:
        return ResponseDto(code=code, message=message, data=None)
