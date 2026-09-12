from pymongo import MongoClient

# Conexión al servidor local en WSL
client = MongoClient("mongodb://localhost:27017/")

# Crear base de datos y colección
db = client["db_local"]
coleccion = db["usuarios"]

# Insertar un documento de prueba
documento = {"nombre": "Irais", "rol": "Estudiante", "estado": "Activo"}
resultado = coleccion.insert_one(documento)

print(f"Documento insertado con ID: {resultado.inserted_id}")