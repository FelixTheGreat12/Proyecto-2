from odmantic import AIOEngine
from motor.motor_asyncio import AsyncIOMotorClient


class Settings:
    MONGODB_URI = "mongodb://localhost:27017"
    DATABASE_NAME = "ESCUELA"

client = AsyncIOMotorClient(Settings.MONGODB_URI)
db = client[Settings.DATABASE_NAME]

async def connect_db():
    # Conectar a la base de datos
    print("Connected to MongoDB")

async def close_db():
    # Cerrar la conexión a la base de datos
    client.close()
    print("Closed MongoDB connection")

# Función para obtener el AIOEngine como dependencia
def get_db():
    return db
