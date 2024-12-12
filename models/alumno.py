from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List
from datetime import datetime
from typing_extensions import Annotated
from bson import ObjectId

PyObjectId = Annotated[str, BeforeValidator(str)]

class AlumnoModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    nombre: str = Field(...)
    apellido: str = Field(...)
    fecha_nacimiento: datetime = Field(...)
    direccion: str = Field(...)
    foto: str = Field(...)
    username: str = Field(...)

class Alumno(AlumnoModel):
    hashed_password: str = Field(...)  # Contraseña encriptada

class UpdateAlumno(BaseModel):
    nombre: Optional[str] = Field(None)
    apellido: Optional[str] = Field(None)
    fecha_nacimiento: Optional[datetime] = Field(None)
    direccion: Optional[str] = Field(None)
    foto: Optional[str] = Field(None)
    password: str = Field(...)  # Contraseña en texto plano
    username: Optional[str] = Field(None)



class AlumnoCollection(BaseModel):
    alumnos: List[AlumnoModel]

