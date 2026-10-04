#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
 Archivo Principal: main.py
 Descripción: Punto de entrada unificado para la suite LogiSmart. Conecta 
              todos los módulos e inicializa la interfaz gráfica de usuario.
==============================================================================
"""

import sys
import tkinter as tk
from tkinter import messagebox

# Importación de los módulos de la arquitectura por capas
try:
    import database
    import rules_engine
    import llm_classifier
    import ethics_evaluator
    from gui import LogiSmartApp
except ImportError as e:
    print(f"[ERROR CRÍTICO] Falta algún módulo dependiente: {e}")
    sys.exit(1)


def verificar_conexiones_previas():
    """Verifica de forma preliminar el estado de las conexiones clave."""
    print("=" * 60)
    print("       INICIANDO SUITE LOGISMART - CENTRO DE CONTROL")
    print("=" * 60)
    
    # Verificar conexión a MongoDB a través del módulo database
    if database.db is not None:
        print("[OK] Conexión establecida correctamente con MongoDB Atlas.")
    else:
        print("[ADVERTENCIA] No se pudo verificar la conexión con MongoDB Atlas. Revisa tu archivo .env.")
    print("-" * 60)


def main():
    """Función principal que ejecuta la aplicación completa."""
    verificar_conexiones_previas()

    try:
        # Inicializar la ventana principal de Tkinter
        root = tk.Tk()
        
        # Instanciar la aplicación gráfica integral contenida en gui.py
        app = LogiSmartApp(root)
        
        # Ejecutar el bucle principal de la interfaz
        root.mainloop()

    except Exception as error:
        print(f"[ERROR] Ocurrió un fallo al ejecutar la interfaz gráfica: {error}")
        try:
            messagebox.showerror("Error de Ejecución", f"No se pudo iniciar la aplicación:\n{error}")
        except Exception:
            pass


if __name__ == "__main__":
    main()