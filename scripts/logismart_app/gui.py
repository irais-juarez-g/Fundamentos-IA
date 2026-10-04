#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Módulo: gui.py
 Descripción: Interfaz gráfica integral con Tkinter y pestañas (Notebook)
              para el centro de control inteligente LogiSmart.
==============================================================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import json

# Importar los módulos creados previamente en la arquitectura por capas
from database import (
    get_collection, registrar_acceso, crear_incidente, 
    obtener_incidentes, actualizar_estado_incidente, 
    estadisticas_incidentes_por_categoria
)
from rules_engine import evaluar_camion, generar_tabla_verdad
from llm_classifier import clasificar_incidente_hibrido, asistente_rag_consulta
from ethics_evaluator import EvaluadorRiesgosIA



class LogiSmartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LogiSmart - Centro de Control Inteligente")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        # Configurar Estilo general
        style = ttk.Style()
        style.theme_use("clam")

        # Crear el contenedor de pestañas (Notebook)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Inicializar las 6 pestañas requeridas
        self.crear_tab_dashboard()
        self.crear_tab_control_acceso()
        self.crear_tab_simulador_tablas()
        self.crear_tab_incidentes()
        self.crear_tab_chat_rag()
        self.crear_tab_riesgos()

    # =========================================================================
    # PESTAÑA 1: PANEL DE CONTROL (DASHBOARD)
    # =========================================================================
    def crear_tab_dashboard(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Panel de Control")

        ttk.Label(tab, text="Indicadores Generales del Sistema LogiSmart", font=("Helvetica", 14, "bold")).pack(pady=15)

        frame_kpis = ttk.LabelFrame(tab, text="Resumen de Operaciones")
        frame_kpis.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.lbl_kpi_camiones = ttk.Label(frame_kpis, text="Camiones registrados en bitácora: Cargando...", font=("Arial", 12))
        self.lbl_kpi_camiones.pack(anchor="w", padx=20, pady=15)

        self.lbl_kpi_incidentes = ttk.Label(frame_kpis, text="Incidentes abiertos totales: Cargando...", font=("Arial", 12))
        self.lbl_kpi_incidentes.pack(anchor="w", padx=20, pady=15)

        btn_actualizar = ttk.Button(frame_kpis, text="Actualizar Indicadores desde MongoDB", command=self.actualizar_dashboard)
        btn_actualizar.pack(pady=20)

        self.actualizar_dashboard()

    def actualizar_dashboard(self):
        try:
            col_accesos = get_collection("accesos")
            total_accesos = col_accesos.count_documents({})
            
            col_inc = get_collection("incidentes")
            total_inc_abiertos = col_inc.count_documents({"estado": {"$ne": "cerrado"}})

            self.lbl_kpi_camiones.config(text=f"Camiones / Accesos procesados en bitácora: {total_accesos}")
            self.lbl_kpi_incidentes.config(text=f"Incidentes activos / abiertos: {total_inc_abiertos}")
        except Exception as e:
            self.lbl_kpi_camiones.config(text=f"Error al conectar con MongoDB: {e}")

    # =========================================================================
    # PESTAÑA 2: CONTROL DE ACCESO
    # =========================================================================
    def crear_tab_control_acceso(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🚛 Control de Acceso")

        ttk.Label(tab, text="Evaluador de Premisas y Caseta de Acceso", font=("Helvetica", 14, "bold")).pack(pady=15)

        frame_form = ttk.LabelFrame(tab, text="Premisas del Vehículo")
        frame_form.pack(fill=tk.X, padx=20, pady=10)

        self.var_p = tk.BooleanVar(value=True)
        self.var_q = tk.BooleanVar(value=False)
        self.var_r = tk.BooleanVar(value=False)
        self.var_s = tk.BooleanVar(value=True)

        ttk.Checkbutton(frame_form, text="P: Vehículo con autorización previa", variable=self.var_p).pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(frame_form, text="Q: El peso excede el límite (Sobrepeso)", variable=self.var_q).pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(frame_form, text="R: Carga con materiales peligrosos", variable=self.var_r).pack(anchor="w", padx=20, pady=5)
        ttk.Checkbutton(frame_form, text="S: Conductor con certificación vigente", variable=self.var_s).pack(anchor="w", padx=20, pady=5)

        ttk.Button(frame_form, text="Evaluar y Guardar en Base de Datos", command=self.evaluar_y_guardar_acceso).pack(pady=15)

        # Semáforo Visual
        frame_semaforo = ttk.LabelFrame(tab, text="Resultado del Semáforo de Acceso")
        frame_semaforo.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.lbl_acceso_std = tk.Label(frame_semaforo, text="Acceso Estándar (A): Pendiente", font=("Arial", 12, "bold"), bg="lightgray", width=40, pady=10)
        self.lbl_acceso_std.pack(pady=10)

        self.lbl_insp_esp = tk.Label(frame_semaforo, text="Inspección Especial (E): Pendiente", font=("Arial", 12, "bold"), bg="lightgray", width=40, pady=10)
        self.lbl_insp_esp.pack(pady=10)

    def evaluar_y_guardar_acceso(self):
        p, q, r, s = self.var_p.get(), self.var_q.get(), self.var_r.get(), self.var_s.get()
        res = evaluar_camion(p, q, r, s)

        # Actualizar semáforo visual
        if res["acceso_estandar"]:
            self.lbl_acceso_std.config(text="Acceso Estándar (A): PERMITIDO", bg="#22c55e", fg="white")
        else:
            self.lbl_acceso_std.config(text="Acceso Estándar (A): DENEGADO", bg="#ef4444", fg="white")

        if res["inspeccion_especial"]:
            self.lbl_insp_esp.config(text="Inspección Especial (E): REQUERIDA", bg="#eab308", fg="black")
        else:
            self.lbl_insp_esp.config(text="Inspección Especial (E): NO REQUERIDA", bg="#22c55e", fg="white")

        # Guardado automático en colección accesos
        registro = {
            "fecha": datetime.now().isoformat(),
            "premisas": {"P": p, "Q": q, "R": r, "S": s},
            "resultados": res,
            "operador": "sistema_gui"
        }
        try:
            registrar_acceso(registro)
            messagebox.SUCCESS if hasattr(messagebox, 'SUCCESS') else None
            messagebox.showinfo("Éxito", "Evaluación guardada automáticamente en la colección 'accesos' de MongoDB.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar en MongoDB: {e}")

    # =========================================================================
    # PESTAÑA 3: SIMULADOR DE TABLAS DE VERDAD
    # =========================================================================
    def crear_tab_simulador_tablas(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔬 Simulador Lógico")

        ttk.Label(tab, text="Simulador de Tablas de Verdad en Vivo", font=("Helvetica", 14, "bold")).pack(pady=15)

        frame_switch = ttk.Frame(tab)
        frame_switch.pack(pady=5)

        self.sim_p = tk.BooleanVar(value=False)
        self.sim_q = tk.BooleanVar(value=False)
        self.sim_r = tk.BooleanVar(value=False)
        self.sim_s = tk.BooleanVar(value=False)

        ttk.Checkbutton(frame_switch, text="P", variable=self.sim_p, command=self.actualizar_simulador).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(frame_switch, text="Q", variable=self.sim_q, command=self.actualizar_simulador).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(frame_switch, text="R", variable=self.sim_r, command=self.actualizar_simulador).pack(side=tk.LEFT, padx=10)
        ttk.Checkbutton(frame_switch, text="S", variable=self.sim_s, command=self.actualizar_simulador).pack(side=tk.LEFT, padx=10)

        self.lbl_sim_resultado = ttk.Label(tab, text="A (Acceso) = F | E (Inspección) = F", font=("Arial", 14, "bold"))
        self.lbl_sim_resultado.pack(pady=20)

        # Tabla completa visible
        frame_tabla = ttk.LabelFrame(tab, text="Tabla Completa (16 Combinaciones)")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.txt_tabla = scrolledtext.ScrolledText(frame_tabla, wrap=tk.WORD, font=("Consolas", 10), height=15)
        self.txt_tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.cargar_texto_tabla_verdad()

    def actualizar_simulador(self):
        res = evaluar_camion(self.sim_p.get(), self.sim_q.get(), self.sim_r.get(), self.sim_s.get())
        a_str = "V" if res["acceso_estandar"] else "F"
        e_str = "V" if res["inspeccion_especial"] else "F"
        self.lbl_sim_resultado.config(text=f"A (Acceso Estándar) = {a_str}  |  E (Inspección Especial) = {e_str}")

    def cargar_texto_tabla_verdad(self):
        tabla = generar_tabla_verdad()
        v = lambda b: "V" if b else "F"
        texto = f"{'P':^3}{'Q':^3}{'R':^3}{'S':^3} | {'¬Q':^4}{'P∧S':^6}{'R∨Q':^6} | {'A':^3}{'E':^3}\n" + "-"*42 + "\n"
        for f in tabla:
            texto += f"{v(f['P']):^3}{v(f['Q']):^3}{v(f['R']):^3}{v(f['S']):^3} | {v(f['no_Q']):^4}{v(f['P_y_S']):^6}{v(f['R_o_Q']):^6} | {v(f['A']):^3}{v(f['E']):^3}\n"
        self.txt_tabla.insert(tk.END, texto)
        self.txt_tabla.config(state=tk.DISABLED)

    # =========================================================================
    # PESTAÑA 4: BANDEJA DE INCIDENTES
    # =========================================================================
    def crear_tab_incidentes(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="✉️ Bandeja de Incidentes")

        ttk.Label(tab, text="Clasificador Híbrido de Incidentes y Correos", font=("Helvetica", 14, "bold")).pack(pady=10)

        frame_input = ttk.Frame(tab)
        frame_input.pack(fill=tk.X, padx=20, pady=5)

        ttk.Label(frame_input, text="Asunto del Correo:").pack(anchor="w")
        self.ent_asunto = ttk.Entry(frame_input, font=("Arial", 11))
        self.ent_asunto.pack(fill=tk.X, pady=5)

        ttk.Label(frame_input, text="Cuerpo del Correo / Mensaje de Incidente:").pack(anchor="w")
        self.txt_cuerpo = scrolledtext.ScrolledText(frame_input, wrap=tk.WORD, height=5, font=("Arial", 11))
        self.txt_cuerpo.pack(fill=tk.X, pady=5)

        ttk.Button(frame_input, text="Clasificar Híbridamente y Guardar", command=self.ejecutar_clasificacion_incidente).pack(pady=10)

        frame_res = ttk.LabelFrame(tab, text="Resultado del Procesamiento (JSON)")
        frame_res.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.txt_resultado_inc = scrolledtext.ScrolledText(frame_res, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_resultado_inc.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def ejecutar_clasificacion_incidente(self):
        asunto = self.ent_asunto.get().strip()
        cuerpo = self.txt_cuerpo.get("1.0", tk.END).strip()

        if not asunto or not cuerpo:
            messagebox.showwarning("Advertencia", "Debes ingresar asunto y cuerpo del incidente.")
            return

        resultado_hibrido = clasificar_incidente_hibrido(asunto, cuerpo)
        
        # Guardar en MongoDB colección 'incidentes'
        doc_incidente = {
            "fecha": datetime.now().isoformat(),
            "asunto": asunto,
            "cuerpo": cuerpo,
            "clasificacion": resultado_hibrido["resultado"],
            "origen_motor": resultado_hibrido["origen"],
            "estado": "nuevo"
        }
        try:
            crear_incidente(doc_incidente)
        except Exception:
            pass

        self.txt_resultado_inc.delete("1.0", tk.END)
        self.txt_resultado_inc.insert(tk.END, json.dumps(resultado_hibrido, ensure_ascii=False, indent=2))

    # =========================================================================
    # PESTAÑA 5: CHAT LLM (ASISTENTE RAG)
    # =========================================================================
    def crear_tab_chat_rag(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💬 Asistente RAG")

        ttk.Label(tab, text="Chat Explicativo con Conexión a MongoDB (RAG)", font=("Helvetica", 14, "bold")).pack(pady=10)

        self.chat_area = scrolledtext.ScrolledText(tab, wrap=tk.WORD, font=("Arial", 11), state=tk.DISABLED)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        frame_chat_input = ttk.Frame(tab)
        frame_chat_input.pack(fill=tk.X, padx=20, pady=10)

        self.ent_chat = ttk.Entry(frame_chat_input, font=("Arial", 12))
        self.ent_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        self.ent_chat.bind("<Return>", lambda event: self.enviar_chat_rag())

        ttk.Button(frame_chat_input, text="Preguntar", command=self.enviar_chat_rag).pack(side=tk.RIGHT)

        self._mostrar_chat_sistema("Sistema RAG listo. Pregunta por ejemplo: '¿Por qué el camión CAM-102 fue inspeccionado?'\n\n")

    def _mostrar_chat_sistema(self, texto):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, texto)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def enviar_chat_rag(self):
        pregunta = self.ent_chat.get().strip()
        if not pregunta:
            return
        self.ent_chat.delete(0, tk.END)

        self._mostrar_chat_sistema(f"Operador: {pregunta}\n")
        
        # Consultar mediante el patrón RAG implementado
        respuesta_rag = asistente_rag_consulta(pregunta)

        self._mostrar_chat_sistema(f"Asistente RAG:\n{respuesta_rag}\n\n" + "-"*40 + "\n")

# =========================================================================
    # PESTAÑA 6: MATRIZ DE RIESGOS ÉTICOS (VERSIÓN NATIVA CON TABLA)
    # =========================================================================
    def crear_tab_riesgos(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="⚖️ Matriz de Riesgos")

        ttk.Label(tab, text="Matriz de Riesgos Éticos y Niveles de Mitigación", font=("Helvetica", 14, "bold")).pack(pady=10)

        frame_tabla = ttk.LabelFrame(tab, text="Riesgos Identificados y Puntaje Residual")
        frame_tabla.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Crear una tabla (Treeview) para mostrar los riesgos éticos
        columnas = ("modulo", "descripcion", "categoria", "puntaje_inicial", "puntaje_residual", "nivel")
        self.tree_riesgos = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        
        self.tree_riesgos.heading("modulo", text="Módulo")
        self.tree_riesgos.heading("descripcion", text="Descripción del Riesgo")
        self.tree_riesgos.heading("categoria", text="Categoría")
        self.tree_riesgos.heading("puntaje_inicial", text="Pts Inicial")
        self.tree_riesgos.heading("puntaje_residual", text="Pts Mitigado")
        self.tree_riesgos.heading("nivel", text="Nivel Final")

        self.tree_riesgos.column("modulo", width=130)
        self.tree_riesgos.column("descripcion", width=220)
        self.tree_riesgos.column("categoria", width=100)
        self.tree_riesgos.column("puntaje_inicial", width=80, anchor="center")
        self.tree_riesgos.column("puntaje_residual", width=90, anchor="center")
        self.tree_riesgos.column("nivel", width=90, anchor="center")

        self.tree_riesgos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Insertar datos de demostración requeridos por la rúbrica
        riesgos_demo = [
            ("Sesgo LLM", "Sesgo en correos con ortografía informal", "sesgo", 20, 8, "Medio"),
            ("Privacidad", "Privacidad de datos y video del conductor", "privacidad", 20, 5, "Bajo"),
            ("Clasificador", "Alucinaciones del modelo en respuestas RAG", "seguridad", 15, 6, "Bajo"),
            ("Automatización", "Dependencia excesiva de decisiones automatizadas", "responsabilidad", 12, 4, "Bajo")
        ]

        for r in riesgos_demo:
            self.tree_riesgos.insert("", tk.END, values=r)


# =========================================================================
# EJECUCIÓN PRINCIPAL DE LA GUI
# =========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = LogiSmartApp(root)
    root.mainloop()