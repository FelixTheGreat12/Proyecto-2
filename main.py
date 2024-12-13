# main.py
from fastapi import FastAPI
from core.mongo import connect_db, close_db, get_db
from api.routes.auth import router as auth_router
from api.routes.profesor import router as profesor_router
from api.routes.alumno import router as alumno_router  # Importamos el router de alumnos
from api.routes.materia import router as materia_router
from api.routes.calificacion import router as calificacion_router  # Importar el router de calificaciones



app = FastAPI()
custom_prefix = "/api/v1"

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# Incluir el router con la dependencia
app.include_router(auth_router, prefix=custom_prefix, tags=["auth"])
app.include_router(profesor_router, prefix=custom_prefix, tags=["profesores"])
app.include_router(alumno_router, prefix=custom_prefix, tags=["alumnos"])  # Agregamos el router de alumnos
app.include_router(materia_router, prefix=custom_prefix, tags=["materias"])
app.include_router(calificacion_router, prefix=custom_prefix, tags=["calificaciones"]) # Agregar el router de calificaciones
