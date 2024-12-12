from fastapi import Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from models.profesor import Profesor
from core.mongo import get_db

async def get_profesor_by_username(username: str, db: AsyncIOMotorClient = Depends(get_db)):
    try:
        if (
          profesor := await db.profesores.find_one({"username": username})
        ) is not None:
          return profesor
        raise HTTPException(status_code=404, detail=f"Profesor{id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
      
async def get_alumno_by_username(username: str, db: AsyncIOMotorClient = Depends(get_db)):
    try:
        if (
         alumno := await db.alumnosfind_one({"username": username})
        ) is not None:
          return alumno
        raise HTTPException(status_code=404, detail=f"Alumno{id} no encontrado")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
