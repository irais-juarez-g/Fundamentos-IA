#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Módulo: ethics_evaluator.py
 Descripción: Gestión de la matriz de riesgos éticos y reportes del sistema IA.
==============================================================================
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class RiesgoEtico:
    """Un riesgo ético asociado a un módulo del sistema."""
    descripcion: str
    categoria: str
    probabilidad: int  # 1 al 5
    impacto: int       # 1 al 5
    mitigacion: str = ""

    @property
    def puntaje(self) -> int:
        """Puntaje de la matriz = probabilidad x impacto."""
        return self.probabilidad * self.impacto

    @property
    def nivel(self) -> str:
        """Clasificación cualitativa según el puntaje."""
        p = self.puntaje
        if p >= 17:
            return "crítico"
        if p >= 10:
            return "alto"
        if p >= 5:
            return "medio"
        return "bajo"


@dataclass
class ModuloIA:
    """Módulo del sistema que se evalúa (con su lista de riesgos)."""
    nombre: str
    descripcion: str = ""
    riesgos: List[RiesgoEtico] = field(default_factory=list)


class EvaluadorRiesgosIA:
    """Registra módulos de un sistema de IA, sus riesgos éticos y genera reportes."""
    CATEGORIAS_VALIDAS = {"sesgo", "privacidad", "transparencia", "seguridad", "responsabilidad", "otro"}

    def __init__(self, nombre_sistema: str) -> None:
        self.nombre_sistema = nombre_sistema
        self._modulos: Dict[str, ModuloIA] = {}

    def registrar_modulo(self, nombre: str, descripcion: str = "") -> ModuloIA:
        """Da de alta un módulo en el evaluador."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del módulo no puede estar vacío")
        if nombre in self._modulos:
            raise ValueError(f"El módulo '{nombre}' ya está registrado")
        modulo = ModuloIA(nombre=nombre.strip(), descripcion=descripcion)
        self._modulos[nombre] = modulo
        return modulo

    def registrar_riesgo(self, modulo: str, descripcion: str, categoria: str,
                         probabilidad: int, impacto: int, mitigacion: str = "") -> RiesgoEtico:
        """Asocia un riesgo ético a un módulo ya registrado."""
        if modulo not in self._modulos:
            raise KeyError(f"El módulo '{modulo}' no existe; regístralo primero")
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoría inválida '{categoria}'. Usa una de {sorted(self.CATEGORIAS_VALIDAS)}")
        for nombre, valor in (("probabilidad", probabilidad), ("impacto", impacto)):
            if not isinstance(valor, int) or isinstance(valor, bool) or not 1 <= valor <= 5:
                raise ValueError(f"{nombre} debe ser un entero entre 1 y 5")
        riesgo = RiesgoEtico(descripcion, categoria, probabilidad, impacto, mitigacion)
        self._modulos[modulo].riesgos.append(riesgo)
        return riesgo

    def todos_los_riesgos(self) -> List[tuple]:
        """Devuelve una lista plana de todos los riesgos ordenada por puntaje descendente."""
        plano = [(m.nombre, r) for m in self._modulos.values() for r in m.riesgos]
        return sorted(plano, key=lambda par: par[1].puntaje, reverse=True)

    def resumen(self) -> Dict[str, object]:
        """Estadísticas agregadas del sistema evaluado."""
        riesgos = self.todos_los_riesgos()
        por_nivel = {"crítico": 0, "alto": 0, "medio": 0, "bajo": 0}
        por_categoria: Dict[str, int] = {}
        for _, r in riesgos:
            por_nivel[r.nivel] += 1
            por_categoria[r.categoria] = por_categoria.get(r.categoria, 0) + 1
        puntajes = [r.puntaje for _, r in riesgos]
        return {
            "sistema": self.nombre_sistema,
            "total_modulos": len(self._modulos),
            "total_riesgos": len(riesgos),
            "riesgos_por_nivel": por_nivel,
            "riesgos_por_categoria": por_categoria,
            "puntaje_promedio": round(sum(puntajes) / len(puntajes), 2) if puntajes else 0,
            "modulos_sin_evaluar": [m.nombre for m in self._modulos.values() if not m.riesgos],
        }

    def reporte_texto(self) -> str:
        """Genera un reporte formateado en texto plano."""
        r = self.resumen()
        L = []
        L.append("=" * 78)
        L.append(f"REPORTE DE RIESGOS ÉTICOS DE IA - {r['sistema']}")
        L.append(f"Generado: {datetime.now():%Y-%m-%d %H:%M}")
        L.append("=" * 78)
        L.append(f"Módulos: {r['total_modulos']} | Riesgos: {r['total_riesgos']} | "
                 f"Puntaje promedio: {r['puntaje_promedio']}")
        L.append("Por nivel: " + ", ".join(f"{k}={v}" for k, v in r["riesgos_por_nivel"].items()))
        L.append("Por categoría: " + (", ".join(f"{k}={v}" for k, v in r["riesgos_por_categoria"].items()) or "-"))
        if r["modulos_sin_evaluar"]:
            L.append("ATENCIÓN - Módulos sin riesgos evaluados: " + ", ".join(r["modulos_sin_evaluar"]))
        L.append("\nMATRIZ (ordenada de mayor a menor riesgo):")
        L.append(f"{'Módulo':<32}{'Riesgo':<34}{'P':>2}{'I':>3}{'Pts':>5}  Nivel")
        L.append("-" * 78)
        for modulo, riesgo in self.todos_los_riesgos():
            L.append(f"{modulo[:31]:<32}{riesgo.descripcion[:33]:<34}"
                     f"{riesgo.probabilidad:>2}{riesgo.impacto:>3}{riesgo.puntaje:>5}  {riesgo.nivel}")
        L.append("\nMITIGACIONES PROPUESTAS:")
        for modulo, riesgo in self.todos_los_riesgos():
            if riesgo.mitigacion:
                L.append(f"  - [{riesgo.nivel.upper()}] {modulo}: {riesgo.mitigacion}")
        return "\n".join(L)

    def exportar_json(self, ruta: Optional[str] = None) -> str:
        """Exporta el reporte completo en formato JSON."""
        datos = {
            "resumen": self.resumen(),
            "modulos": [
                {"nombre": m.nombre, "descripcion": m.descripcion,
                 "riesgos": [{**asdict(r), "puntaje": r.puntaje, "nivel": r.nivel} for r in m.riesgos]}
                for m in self._modulos.values()
            ],
        }
        texto = json.dumps(datos, ensure_ascii=False, indent=2)
        if ruta:
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(texto)
        return texto

    def exportar_texto(self, ruta: str) -> None:
        """Guarda el reporte de texto en un archivo .txt."""
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(self.reporte_texto())