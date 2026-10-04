#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Módulo: rules_engine.py
 Descripción: Motor de reglas lógicas y tablas de verdad ampliadas.
==============================================================================
"""

import itertools
from typing import Dict, List

def evaluar_camion(P: bool, Q: bool, R: bool, S: bool, T: bool = True, H: bool = True) -> Dict[str, bool]:
    """
    Evalúa las reglas de acceso, inspección y las nuevas reglas logísticas.

    Premisas base:
      P: Vehículo con autorización previa
      Q: El peso excede el límite
      R: Carga con materiales peligrosos
      S: Conductor con certificación vigente
    Nuevas premisas para las reglas ampliadas:
      T: Documentación de certificación física al día (sin bloqueos administrativos)
      H: Ingreso dentro del horario permitido para materiales peligrosos
    """
    # Validación defensiva de tipos booleanos
    for nombre, valor in (("P", P), ("Q", Q), ("R", R), ("S", S), ("T", T), ("H", H)):
        if not isinstance(valor, bool):
            raise TypeError(f"La premisa {nombre} debe ser bool, se recibió {type(valor).__name__}")

    # Regla Base 1: Acceso Estándar (A = P ∧ S ∧ ¬Q)
    acceso_estandar = P and S and (not Q)

    # Regla Base 2: Inspección Especial (E = P ∧ (R ∨ Q))
    inspeccion_especial = P and (R or Q)

    # --- NUEVA REGLA 1: Vigencia estricta de certificación (V = P ∧ S ∧ T ∧ ¬Q) ---
    vigencia_certificacion = P and S and T and (not Q)

    # --- NUEVA REGLA 2: Horario restringido para materiales peligrosos (H_mat = ¬R ∨ (R ∧ H)) ---
    # Si transporta materiales peligrosos (R), obligatoriamente debe estar en horario permitido (H).
    horario_materiales_peligrosos = not R or (R and H)

    return {
        "acceso_estandar": acceso_estandar,
        "inspeccion_especial": inspeccion_especial,
        "vigencia_certificacion": vigencia_certificacion,
        "horario_materiales_peligrosos": horario_materiales_peligrosos
    }


def generar_tabla_verdad() -> List[Dict[str, bool]]:
    """Genera la tabla de verdad completa para las variables principales (P, Q, R, S)."""
    filas: List[Dict[str, bool]] = []
    for P, Q, R, S in itertools.product([True, False], repeat=4):
        resultado = evaluar_camion(P, Q, R, S)
        filas.append({
            "P": P, "Q": Q, "R": R, "S": S,
            "no_Q": not Q,
            "P_y_S": P and S,
            "R_o_Q": R or Q,
            "A": resultado["acceso_estandar"],
            "E": resultado["inspeccion_especial"],
            "V": resultado["vigencia_certificacion"],
            "H_mat": resultado["horario_materiales_peligrosos"]
        })
    return filas


def imprimir_tablas_verdad() -> None:
    """Imprime las tablas de verdad en consola incluyendo las reglas ampliadas."""
    v = lambda b: "V" if b else "F"
    tabla = generar_tabla_verdad()

    print("=" * 78)
    print("MOTOR DE REGLAS - TABLAS DE VERDAD AMPLIADAS")
    print("=" * 78)
    print(f"{'P':^3}{'Q':^3}{'R':^3}{'S':^3} | {'¬Q':^4}{'P∧S':^6}{'R∨Q':^6} | {'A':^3}{'E':^3}{'V':^3}{'H_mat':^6}")
    print("-" * 55)
    for f in tabla:
        print(f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['R']):^3}{v(f['S']):^3} | "
              f"{v(f['no_Q']):^4}{v(f['P_y_S']):^6}{v(f['R_o_Q']):^6} | "
              f"{v(f['A']):^3}{v(f['E']):^3}{v(f['V']):^3}{v(f['H_mat']):^6}")
    print()