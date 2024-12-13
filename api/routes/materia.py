from fastapi import APIRouter, Depends, HTTPException, Body, status
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo import ReturnDocument
from fastapi.responses import Response
from typing import List
from models.materia import MateriaModel, Materia, MateriaCollection, UpdateMateria
from core.mongo import get_db
import datetime

router = APIRouter()

@router.post(
    "/materias", 
    response_description="Agregar nueva Materia",
    response_model=MateriaModel,
    status_code=status.HTTP_201_CREATED
)
async def post_materia(materia: Materia = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    new_materia = await db.materias.insert_one({
        **materia.dict(exclude_unset=True),
    })
    created_materia = await db.materias.find_one({"_id": new_materia.inserted_id})
    return created_materia

@router.get(
    "/materias",
    response_description="Lista de todas las materias",
    response_model=MateriaCollection
)
async def get_all_materias(db: AsyncIOMotorClient = Depends(get_db)):
    materias = await db.materias.find().to_list(1000)
    return MateriaCollection(materias=materias)

@router.get(
    "/materias/{id}",
    response_description="Obtener una materia",
    response_model=MateriaModel
)
async def get_materia_by_id(id: str, db: AsyncIOMotorClient = Depends(get_db)):
    if (materia := await db.materias.find_one({"_id": ObjectId(id)})) is not None:
        return materia
    raise HTTPException(status_code=404, detail=f"Materia {id} no encontrada")

@router.put(
    "/materias/{id}",
    response_description="Actualizar materia",
    response_model=MateriaModel
)
async def update_materia(id: str, materia: UpdateMateria = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    materia_data = {
        k: v for k, v in materia.dict(exclude_unset=True).items() if v is not None
    }
    if len(materia_data) >= 1:
        update_result = await db.materias.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": materia_data},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Materia {id} no encontrada")
    raise HTTPException(status_code=400, detail="No se proporcionaron datos para actualizar")

@router.delete("/materias/{id}", response_description="Eliminar Materia")
async def delete_materia(id: str, db: AsyncIOMotorClient = Depends(get_db)):
    delete_result = await db.materias.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Materia {id} no encontrada")

@router.post(
    "/materias/{id_materia}/asignar",
    response_description="Asignar materia a un profesor",
    status_code=status.HTTP_201_CREATED
)
async def asignar_materia_a_profesor(
    id_materia: str,
    id_profesor: str = Body(..., embed=True),
    db: AsyncIOMotorClient = Depends(get_db)
):
    # Verifica que la materia exista
    if not await db.materias.find_one({"_id": ObjectId(id_materia)}):
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Verifica que el profesor exista
    if not await db.profesores.find_one({"_id": ObjectId(id_profesor)}):
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    # Crea la asignación
    nueva_asignacion = {
        "id_materia": ObjectId(id_materia),
        "id_profesor": ObjectId(id_profesor),
        "fecha_asignacion": datetime.utcnow(),
    }
    result = await db.asignaciones.insert_one(nueva_asignacion)

    return {"id": str(result.inserted_id), **nueva_asignacion}

