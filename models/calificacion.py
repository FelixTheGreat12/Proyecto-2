from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId
from datetime import datetime

PyObjectId = Annotated[str, BeforeValidator(str)]

class CalificacionModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    id_alumno: PyObjectId = Field(...)
    id_materia: PyObjectId = Field(...)
    calificacion: float = Field(...)
    fecha_calificacion: datetime = Field(default_factory=datetime.utcnow)


class Calificacion(CalificacionModel):
    pass


class UpdateCalificacion(BaseModel):
    calificacion: Optional[float] = Field(None)


class CalificacionCollection(BaseModel):
    calificaciones: List[CalificacionModel]