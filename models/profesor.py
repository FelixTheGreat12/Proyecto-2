from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List
from datetime import datetime
from typing import Optional
from typing_extensions import Annotated
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class ProfesorModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    nombre: str = Field(...)
    apellido: str = Field(...)
    username: str = Field(...)
    fecha_nacimiento: datetime = Field(...)
    direccion: str = Field(...)
    especialidad: str  = Field(...)
    
class Profesor(ProfesorModel):
    hashed_password: str = Field(...)
    
class UpdateProfesor(BaseModel):
    nombre: Optional[str] = Field(None)
    apellido: Optional[str] = Field(None)
    username: Optional[str] = Field(None)
    fecha_nacimiento: Optional[datetime] = Field(None)
    direccion: Optional[str] = Field(None)
    especialidad: Optional[str] = Field(None)
    
class ProfesorCollection(BaseModel):
    profesores: List[ProfesorModel]