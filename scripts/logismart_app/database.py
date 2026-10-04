#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Módulo: database.py
 Descripción: Conexión a MongoDB Atlas y operaciones CRUD + Agregaciones.
==============================================================================
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

# Cargar las variables del archivo .env
load_dotenv()

MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")
MONGO_DB_NAME = os.getenv("MONGO_DB", "irais")

# Construir la URI de conexión oficial para MongoDB Atlas
MONGO_URI = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/?retryWrites=true&w=majority"

db = None
try:
    # Inicializar cliente de MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    
    # Verificar conexión haciendo un ping rápido
    client.admin.command('ping')
    print("¡Conexión exitosa a MongoDB Atlas!")
    
except Exception as e:
    print(f"Error al conectar con MongoDB Atlas: {e}")

def get_collection(nombre_coleccion):
    """Devuelve la colección solicitada si hay conexión activa."""
    if db is not None:
        return db[nombre_coleccion]
    raise ConnectionError("No hay conexión activa con la base de datos.")


# =============================================================================
# OPERACIONES CRUD POR COLECCIÓN
# =============================================================================

# --- 1. COLECCIÓN: camiones ---
def crear_camion(data: dict):
    return get_collection("camiones").insert_one(data)

def obtener_camiones(filtro: dict = None):
    return list(get_collection("camiones").find(filtro or {}))

def actualizar_camion(filtro: dict, nuevos_datos: dict):
    return get_collection("camiones").update_one(filtro, {"$set": nuevos_datos})

def eliminar_camion(filtro: dict):
    return get_collection("camiones").delete_one(filtro)


# --- 2. COLECCIÓN: accesos (Bitácora de validaciones P, Q, R, S) ---
def registrar_acceso(data: dict):
    return get_collection("accesos").insert_one(data)

def obtener_accesos(filtro: dict = None):
    return list(get_collection("accesos").find(filtro or {}))


# --- 3. COLECCIÓN: incidentes (Estados: nuevo, en_atencion, cerrado) ---
def crear_incidente(data: dict):
    if "estado" not in data:
        data["estado"] = "nuevo"  # Estado por defecto requerido
    return get_collection("incidentes").insert_one(data)

def obtener_incidentes(filtro: dict = None):
    return list(get_collection("incidentes").find(filtro or {}))

def actualizar_estado_incidente(incidente_id: str, nuevo_estado: str):
    return get_collection("incidentes").update_one(
        {"_id": ObjectId(incidente_id)}, 
        {"$set": {"estado": nuevo_estado}}
    )

def eliminar_incidente(incidente_id: str):
    return get_collection("incidentes").delete_one({"_id": ObjectId(incidente_id)})


# --- 4. COLECCIÓN: riesgos_eticos ---
def registrar_riesgo_db(data: dict):
    return get_collection("riesgos_eticos").insert_one(data)

def obtener_riesgos_db(filtro: dict = None):
    return list(get_collection("riesgos_eticos").find(filtro or {}))

def actualizar_riesgo_db(filtro: dict, nuevos_datos: dict):
    return get_collection("riesgos_eticos").update_one(filtro, {"$set": nuevos_datos})

def eliminar_riesgo_db(filtro: dict):
    return get_collection("riesgos_eticos").delete_one(filtro)


# --- 5. COLECCIÓN: evaluaciones_llm ---
def registrar_evaluacion_llm(data: dict):
    return get_collection("evaluaciones_llm").insert_one(data)

def obtener_evaluaciones_llm(filtro: dict = None):
    return list(get_collection("evaluaciones_llm").find(filtro or {}))


# =============================================================================
# FUNCIÓN DE AGREGACIÓN DE MONGODB ($match y $group)
# =============================================================================
def estadisticas_incidentes_por_categoria(categoria_filtro: str = None):
    """
    Utiliza un pipeline de agregación para contar incidentes agrupados por categoría.
    - $match: Filtra opcionalmente por una categoría específica si se proporciona.
    - $group: Agrupa por la categoría del incidente y calcula el total de ocurrencias.
    """
    coleccion = get_collection("incidentes")
    pipeline = []
    
    # 1. Etapa $match (Filtro previo opcional)
    if categoria_filtro:
        pipeline.append({"$match": {"clasificacion.categoria": categoria_filtro}})
        
    # 2. Etapa $group (Agrupación y conteo)
    pipeline.append({
        "$group": {
            "_id": "$clasificacion.categoria",
            "total_incidentes": {"$sum": 1},
            "registros": {"$push": "$$ROOT"}
        }
    })
    
    return list(coleccion.aggregate(pipeline))