from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ResponsableBase(BaseModel):
    nombre_completo: str = Field(..., description="Nombre canónico oficial")
    alias_conocidos: List[str] = Field(default_factory=list, description="Variantes y apodos reconocibles por la IA")
    email: Optional[str] = None
    rol: Optional[str] = None
    activo: bool = True

class ResponsableCreate(ResponsableBase):
    proyecto_id: Optional[str] = "PROJ-DEFAULT"

class ResponsableResponse(ResponsableBase):
    id: str
    proyecto_id: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True
