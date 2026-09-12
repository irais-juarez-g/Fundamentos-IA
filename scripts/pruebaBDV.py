import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Cargar archivo .env
load_dotenv()

usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

# IMPRESIÓN DE PRUEBA (Para verificar qué variable falla)
print(f"Usuario: {usuario} | Cluster: {cluster}")

if not cluster:
    raise ValueError("Error: No se pudo leer la variable MONGO_CLUSTER del archivo .env")

mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"