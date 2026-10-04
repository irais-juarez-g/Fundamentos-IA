#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Módulo: llm_classifier.py
 Descripción: Clasificador híbrido (Reglas + LLM con Ollama y Pydantic)
              y Asistente RAG conectado a MongoDB.
==============================================================================
"""

import json
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError
import ollama
from database import get_collection

# =============================================================================
# 1. ESQUEMA PYDANTIC PARA VALIDACIÓN ESTRICTA DEL JSON DEL LLM
# =============================================================================
class EntidadesExtraidas(BaseModel):
    placa: Optional[str] = None
    camion_id: Optional[str] = None
    peso_reportado_kg: Optional[float] = None
    ubicacion: Optional[str] = None

class IncidenteSchema(BaseModel):
    categoria: str = Field(..., description="Categoría del incidente")
    prioridad: str = Field(..., description="Prioridad del incidente (baja, media, alta, critica)")
    entidades: EntidadesExtraidas
    resumen: str = Field(..., description="Breve resumen del incidente")


# =============================================================================
# 2. CLASIFICADOR POR REGLAS (FALLBACK DEL CÓDIGO ORIGINAL)
# =============================================================================
CATEGORIAS: Dict[str, List[str]] = {
    "materiales_peligrosos": ["peligroso", "derrame", "fuga", "quimico", "inflamable", "toxico", "corrosivo"],
    "sobrepeso": ["sobrepeso", "excede", "bascula", "exceso de peso", "sobrecarga"],
    "acceso_no_autorizado": ["sin autorizacion", "no autorizado", "acceso denegado", "barrera", "intruso"],
    "falla_hardware": ["camara", "sensor", "lector", "rfid", "no enciende", "apagado", "danado", "falla electrica"],
    "falla_software": ["sistema", "error", "pantalla", "caido", "no carga", "lento", "software", "aplicacion"],
    "somnolencia_conductor": ["somnolencia", "dormido", "cansancio", "fatiga", "sueno"],
}

PALABRAS_URGENTES = ["urgente", "emergencia", "accidente", "incendio", "herido", "critico", "inmediato"]
PRIORIDAD_BASE: Dict[str, str] = {
    "materiales_peligrosos": "critica",
    "somnolencia_conductor": "alta",
    "acceso_no_autorizado": "alta",
    "sobrepeso": "media",
    "falla_hardware": "media",
    "falla_software": "baja",
    "otro": "baja",
}
ORDEN_PRIORIDAD = ["baja", "media", "alta", "critica"]

def _normalizar(texto: str) -> str:
    tabla = str.maketrans("áéíóúüñ", "aeiouun")
    return texto.lower().translate(tabla)

def clasificador_por_reglas(asunto: str, cuerpo: str) -> dict:
    """Clasificador de respaldo basado estrictamente en reglas y expresiones regulares."""
    texto = _normalizar(f"{asunto} {cuerpo}")
    puntajes = {cat: [kw for kw in kws if kw in texto] for cat, kws in CATEGORIAS.items()}
    mejor_cat = max(puntajes, key=lambda c: len(puntajes[c]))
    if not puntajes[mejor_cat]:
        mejor_cat = "otro"
    
    prioridad = PRIORIDAD_BASE[mejor_cat]
    if any(p in texto for p in PALABRAS_URGENTES):
        idx = min(ORDEN_PRIORIDAD.index(prioridad) + 1, len(ORDEN_PRIORIDAD) - 1)
        prioridad = ORDEN_PRIORIDAD[idx]

    m_placa = re.search(r"\b[A-Z0-9]{2,3}-\d{2,3}-[A-Z0-9]{1,2}\b", texto.upper())
    m_camion = re.search(r"\bCAM-\d+\b", texto.upper())
    m_peso = re.search(r"(\d+(?:[.,]\d+)?)\s*(toneladas|tonelada|ton|t|kg)\b", texto.lower())
    peso_kg = None
    if m_peso:
        val = float(m_peso.group(1).replace(",", "."))
        peso_kg = val if m_peso.group(2) == "kg" else val * 1000
    m_ubic = re.search(r"\b(and[eé]n|puerta|muelle|caseta|dock)\s+([A-Za-z0-9]+)", texto, re.IGNORECASE)

    return {
        "categoria": mejor_cat,
        "prioridad": prioridad,
        "entidades": {
            "placa": m_placa.group(0) if m_placa else None,
            "camion_id": m_camion.group(0) if m_camion else None,
            "peso_reportado_kg": peso_kg,
            "ubicacion": f"{m_ubic.group(1)} {m_ubic.group(2)}".lower() if m_ubic else None
        },
        "resumen": f"Incidente clasificado por reglas como {mejor_cat} con prioridad {prioridad}."
    }


# =============================================================================
# 3. CLASIFICADOR HÍBRIDO (OLLAMA + PYDANTIC + REINTENTOS + FALLBACK)
# =============================================================================
def clasificar_incidente_hibrido(asunto: str, cuerpo: str, modelo: str = "llama3.2:1b") -> dict:
    """
    Envía el correo al LLM local (Ollama) solicitando un JSON. Valida estrictamente 
    con Pydantic. Si falla tras reintentos, ejecuta el fallback por reglas.
    """
    prompt = f"""
    Eres un clasificador logístico experto. Analiza el correo de incidente y devuelve UNICAMENTE un objeto JSON válido con este esquema exacto:
    {{
      "categoria": "materiales_peligrosos | sobrepeso | acceso_no_autorizado | falla_hardware | falla_software | somnolencia_conductor | otro",
      "prioridad": "baja | media | alta | critica",
      "entidades": {{
        "placa": "string o null",
        "camion_id": "string o null",
        "peso_reportado_kg": "number o null",
        "ubicacion": "string o null"
      }},
      "resumen": "string breve"
    }}

    Asunto: {asunto}
    Cuerpo: {cuerpo}
    """

    intentos = 2
    for intento in range(intentos):
        try:
            respuesta = ollama.chat(
                model=modelo,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            contenido = respuesta["message"]["content"]
            
            # Limpiar bloques de código markdown si los incluye el LLM
            limpio = re.sub(r"```json\s*|\s*```", "", contenido).strip()
            datos_json = json.loads(limpio)
            
            # Validación estricta con Pydantic
            validado = IncidenteSchema(**datos_json)
            return {
                "origen": "llm",
                "resultado": validado.dict()
            }
        except (json.JSONDecodeError, ValidationError, Exception):
            if intento == intentos - 1:
                # Fallback hacia el clasificador por reglas si falla la validación
                fallback_res = clasificador_por_reglas(asunto, cuerpo)
                return {
                    "origen": "fallback_reglas",
                    "resultado": fallback_res
                }


# =============================================================================
# 4. ASISTENTE RAG SENCILLO (MONGODB + OLLAMA)
# =============================================================================
def asistente_rag_consulta(pregunta: str, modelo: str = "llama3.2:1b") -> str:
    """
    Busca registros relacionados de forma flexible en MongoDB y pasa el contexto al LLM. 
    Si no hay datos, responde estrictamente 'no tengo información'.
    """
    match_camion = re.search(r"\bCAM-\d+\b", pregunta.upper())
    match_placa = re.search(r"\b[A-Z0-9]{2,3}-\d{2,3}-[A-Z0-9]{1,2}\b", pregunta.upper())

    filtro = {}
    if match_camion:
        c_id = match_camion.group(0)
        filtro["$or"] = [
            {"camion_id": c_id},
            {"datos_extraidos.camion_id": c_id},
            {"clasificacion.entidades.camion_id": c_id},
            {"cuerpo": {"$regex": c_id, "$options": "i"}}
        ]
    elif match_placa:
        p_id = match_placa.group(0)
        filtro["$or"] = [
            {"placa": p_id},
            {"datos_extraidos.placa": p_id},
            {"clasificacion.entidades.placa": p_id},
            {"cuerpo": {"$regex": p_id, "$options": "i"}}
        ]

    contexto_datos = []
    try:
        col_accesos = get_collection("accesos")
        docs_accesos = list(col_accesos.find(filtro, {"_id": 0})) if filtro else list(col_accesos.find({}, {"_id": 0}).limit(5))
        contexto_datos.extend(docs_accesos)

        col_incidentes = get_collection("incidentes")
        # Si no hubo un camión o placa específica en la pregunta, traemos los incidentes recientes
        docs_inc = list(col_incidentes.find(filtro, {"_id": 0})) if filtro else list(col_incidentes.find({}, {"_id": 0}).sort("_id", -1).limit(3))
        contexto_datos.extend(docs_inc)
    except Exception:
        pass

    # Si aún no hay registros, permitimos enviar los últimos documentos generales para que el LLM tenga contexto
    if not contexto_datos:
        try:
            docs_gen = list(get_collection("incidentes").find({}, {"_id": 0}).limit(3))
            contexto_datos.extend(docs_gen)
        except Exception:
            pass

    if not contexto_datos:
        return "no tengo información"

    contexto_str = json.dumps(contexto_datos, ensure_ascii=False, indent=2)
    
    prompt_rag = f"""
    Eres un asistente del centro logístico experto. Responde a la pregunta del operador basándote EXCLUSIVAMENTE en los registros recuperados de MongoDB adjuntos abajo. Cita de qué registro o incidente obtuviste la información. Si la respuesta definitiva no se encuentra en estos datos, responde estrictamente "no tengo información".

    Registros de Base de Datos:
    {contexto_str}

    Pregunta del operador: {pregunta}
    """

    try:
        respuesta = ollama.chat(
            model=modelo,
            messages=[{"role": "user", "content": prompt_rag}],
            options={"temperature": 0.1}
        )
        return respuesta["message"]["content"]
    except Exception:
        return "no tengo información"