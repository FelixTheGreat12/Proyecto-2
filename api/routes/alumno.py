from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, Depends, HTTPException, Body, status
from bson import ObjectId
from pymongo import ReturnDocument
from fastapi.responses import Response
from typing import List
from core.security import decode_access_token
from core.mongo import get_db
from models.alumno import AlumnoModel, Alumno, AlumnoCollection, UpdateAlumno
from fastapi.security import OAuth2PasswordBearer
import datetime


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/api/v1/token")
router = APIRouter()

async def get_current_alumno(engine: AsyncIOMotorClient = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    alumno = await engine.alumnos.find_one({"username": username})

    if not alumno:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return AlumnoModel(**alumno)

@router.post(
    "/alumnos", 
    response_description="Agregar nuevo Alumno",
    response_model=AlumnoModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_alumno)]
)
async def post_alumno(alumno: Alumno = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    hashed_password = pwd_context.hash(alumno.hashed_password)
    alumno.hashed_password = hashed_password
    new_alumno = await db.alumnos.insert_one({
        **alumno.dict(exclude_unset=True),                                                                                                                                             
    })
    created_alumno = await db.alumnos.find_one({"_id": new_alumno.inserted_id})
    return created_alumno

@router.get(
    "/alumnos",
    response_description="Lista de todos los alumnos",
    response_model=AlumnoCollection,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_alumno)]
)
async def get_all_alumnos(db: AsyncIOMotorClient = Depends(get_db)):
    return AlumnoCollection(alumnos=await db.alumnos.find().to_list(1000))

@router.get(
    "/alumnos/{id}",
    response_description="Obtener un alumno",
    response_model=AlumnoModel,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_alumno)]
)
async def get_alumno_by_id(id: str, db: AsyncIOMotorClient = Depends(get_db)):
    if (
        alumno := await db.alumnos.find_one({"_id": ObjectId(id)})
    ) is not None:
        return alumno
    raise HTTPException(status_code=404, detail=f"Alumno {id} no encontrado")

@router.put(
    "/alumnos/{id}",
    response_description="Actualizar alumno",
    response_model=AlumnoModel,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_alumno)]
)
async def update_alumno(id: str, alumno: UpdateAlumno = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    alumno = {
        k: v for k, v in alumno.model_dump(by_alias=True).items() if v is not None
    }
    if len(alumno) >= 1:
        update_result = await db.alumnos.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": alumno},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Alumno {id} no encontrado")
    if (existing_alumno := await db.alumnos.find_one({"_id": id})) is not None:
        return existing_alumno
    raise HTTPException(status_code=404, detail=f"Alumno {id} no encontrado")

@router.delete("/alumnos/{id}", response_description="Eliminar Alumno", dependencies=[Depends(get_current_alumno)])
async def delete_alumno(id: str, db: AsyncIOMotorClient = Depends(get_db)):
    delete_result = await db.alumnos.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Alumno {id} no encontrado")

@router.post(
    "/alumnos/{id_alumno}/inscribir",
    response_description="Inscribir alumno a una materia",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_alumno)]  # Requiere autenticación
)
async def inscribir_alumno_a_materia(
    id_alumno: str,
    id_materia: str = Body(..., embed=True),
    db: AsyncIOMotorClient = Depends(get_db)
):
    # Verifica que el alumno exista
    if not await db.alumnos.find_one({"_id": ObjectId(id_alumno)}):
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # Verifica que la materia exista
    if not await db.materias.find_one({"_id": ObjectId(id_materia)}):
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Crea la inscripción
    nueva_inscripcion = {
        "id_alumno": ObjectId(id_alumno),
        "id_materia": ObjectId(id_materia),
        "fecha_inscripcion": datetime.datetime.utcnow(),
    }
    result = await db.inscripciones.insert_one(nueva_inscripcion)

    return {"id": str(result.inserted_id), **nueva_inscripcion}

