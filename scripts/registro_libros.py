import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from pyspark.sql import SparkSession

# 1. Cargar credenciales
load_dotenv()
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

# Variables globales para la conexión
mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"

def guardar_animal():
    """Captura los datos del formulario y los guarda en Atlas"""
    nombre = entry_nombre.get()
    especie = entry_especie.get()
    edad = entry_edad.get()

    # Validar que no estén vacíos
    if not nombre or not especie or not edad:
        messagebox.showwarning("Campos incompletos", "Por favor, llena todos los datos del animal.")
        return

    try:
        # Conectar a la base de datos y guardar
        cliente = MongoClient(mongo_url)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        nuevo_animal = {
            "nombre": nombre,
            "especie": especie,
            "edad": int(edad)
        }
        
        coleccion.insert_one(nuevo_animal)
        messagebox.showinfo("Éxito", f"¡{nombre} guardado en la nube correctamente!")
        
        # Limpiar los campos de texto
        entry_nombre.delete(0, tk.END)
        entry_especie.delete(0, tk.END)
        entry_edad.delete(0, tk.END)
        
        # Actualizar la tabla visual
        cargar_datos()
        
    except ValueError:
        messagebox.showerror("Error", "La edad debe ser un número entero.")
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"No se pudo guardar:\n{e}")

def cargar_datos():
    """Descarga los datos de Atlas y los muestra usando PySpark"""
    try:
        cliente = MongoClient(mongo_url)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        documentos = list(coleccion.find({}, {"_id": 0}))
        
        if not documentos:
            return

        spark = SparkSession.builder.appName("TkinterSpark").getOrCreate()
        df = spark.createDataFrame(documentos)
        
        for item in tabla.get_children():
            tabla.delete(item)
            
        columnas = df.columns
        tabla["columns"] = columnas
        tabla["show"] = "headings"
        
        for col in columnas:
            tabla.heading(col, text=col.capitalize())
            tabla.column(col, width=120, anchor="center")
            
        filas = df.collect()
        for fila in filas:
            valores = [fila[c] for c in columnas]
            tabla.insert("", "end", values=valores)
            
    except Exception as e:
        messagebox.showerror("Error", f"Problema al cargar datos:\n{e}")

# --- Configuración de la Interfaz Gráfica ---
ventana = tk.Tk()
ventana.title("Registro Clínico - Atlas + PySpark")
ventana.geometry("600x500")

# --- Sección 1: Formulario de Captura ---
marco_formulario = tk.LabelFrame(ventana, text="Registrar Nuevo Animal", padx=10, pady=10)
marco_formulario.pack(fill="x", padx=20, pady=10)

# Campos de texto (Labels y Entries)
tk.Label(marco_formulario, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
entry_nombre = tk.Entry(marco_formulario)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)

tk.Label(marco_formulario, text="Especie:").grid(row=0, column=2, padx=5, pady=5)
entry_especie = tk.Entry(marco_formulario)
entry_especie.grid(row=0, column=3, padx=5, pady=5)

tk.Label(marco_formulario, text="Edad:").grid(row=0, column=4, padx=5, pady=5)
entry_edad = tk.Entry(marco_formulario, width=5)
entry_edad.grid(row=0, column=5, padx=5, pady=5)

# Botón Guardar
btn_guardar = tk.Button(marco_formulario, text="Guardar en Atlas", command=guardar_animal, bg="lightblue")
btn_guardar.grid(row=1, column=0, columnspan=6, pady=10)

# --- Sección 2: Visualización de Datos ---
btn_cargar = tk.Button(ventana, text="Refrescar Datos de la Nube", command=cargar_datos)
btn_cargar.pack(pady=5)

marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=10)

tabla = ttk.Treeview(marco_tabla)
tabla.pack(expand=True, fill="both")

# Cargar los datos automáticamente al abrir la ventana
cargar_datos()

ventana.mainloop()