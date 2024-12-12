from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, Depends, HTTPException, Body, status
from bson import ObjectId
from pymongo import ReturnDocument
from fastapi.responses import Response
from typing import List
from core.security import decode_access_token
from core.mongo import get_db
from models.profesor import ProfesorModel, Profesor, ProfesorCollection, UpdateProfesor
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8000/api/v1/token")
router = APIRouter()

async def get_current_profesor(engine: AsyncIOMotorClient = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)  # Asumimos que tienes esta función definida
    username = payload.get("sub")

    if not username:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Buscamos al profesor en la colección "profesores" usando Motor
    profesor = await engine.profesores.find_one({"username": username})

    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    return ProfesorModel(**profesor)

@router.post(
    "/profesores", 
    response_description="Agregar nuevo Profesor",
    response_model=ProfesorModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_profesor)]
)
async def post_profesor(profesor: Profesor = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    hashed_password = pwd_context.hash(profesor.hashed_password)
    profesor.hashed_password = hashed_password

    new_profesor = await db.profesores.insert_one({
        **profesor.dict(exclude_unset=True),                                                                                                                                            
    })
    created_profesor = await db.profesores.find_one({"_id": new_profesor.inserted_id})
    return created_profesor

@router.get(
    "/profesores",
    response_description="Lista de todos los profesores",
    response_model=ProfesorCollection,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_profesor)]
)
async def get_all_profesores(db: AsyncIOMotorClient = Depends(get_db)):
    return ProfesorCollection(profesores=await db.profesores.find().to_list(1000))

@router.get(
    "/profesores/{id}",
    response_description="Obtener un profesor",
    response_model=ProfesorModel,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_profesor)]
)
async def get_profesor_by_id(id: str, db: AsyncIOMotorClient = Depends(get_db)):
    if (
        profesor := await db.profesores.find_one({"_id": ObjectId(id)})
    ) is not None:
        return profesor
    raise HTTPException(status_code=404, detail=f"Profesor{id} no encontrado")

@router.put(
    "/profesores/{id}",
    response_description="Actualizar profesor",
    response_model=ProfesorModel,
    response_model_by_alias=False,
    dependencies=[Depends(get_current_profesor)]
)
async def update_profesor(id: str, profesor: UpdateProfesor = Body(...), db: AsyncIOMotorClient = Depends(get_db)):
    profesor = {
        k: v for k, v in profesor.model_dump(by_alias=True).items() if v is not None
    }
    if len(profesor) >= 1:
        update_result = await db.profesores.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": profesor},
            return_document=ReturnDocument.AFTER,
        )
        if update_result is not None:
            return update_result
        else:
            raise HTTPException(status_code=404, detail=f"Profesor {id} no encontrado")
    if (existing_profesor := await db.profesores.find_one({"_id": id})) is not None:
        return existing_profesor
    raise HTTPException(status_code=404, detail=f"Profesor {id} no encontrado")

@router.delete("/profesores/{id}", response_description="Eliminar Profesor", dependencies=[Depends(get_current_profesor)])
async def delete_profesor(id: str,  db: AsyncIOMotorClient = Depends(get_db)):
    delete_result = await db.profesores.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Profesor {id} no encontrado")