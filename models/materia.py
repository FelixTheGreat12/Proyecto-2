from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, List
from datetime import datetime
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

# Modelo para representar la Materia
class MateriaModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    nombre: str = Field(...)
    descripcion: str = Field(...)
    

# Para crear una nueva Materia (sin id)
class Materia(MateriaModel):
    pass

# Para actualizar una Materia (pueden ser campos opcionales)
class UpdateMateria(BaseModel):
    nombre: Optional[str] = Field(None)
    descripcion: Optional[str] = Field(None)

# Colección de Materias
class MateriaCollection(BaseModel):
    materias: List[MateriaModel]
