import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient

# --- 1. Cargar Credenciales de la Base de Datos ---
load_dotenv()
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION") # <-- Volvemos a usar la colección del .env

# Construir URL de conexión
mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"

# --- 2. Lógica del Agente Reactivo ---
class AgenteClimatizacion:
    def __init__(self):
        self.temperatura = 0.0
        self.humedad = 0.0
        self.accion = ""

    def tomar_decision(self, temp, hum):
        self.temperatura = temp
        self.humedad = hum
        
        if self.temperatura > 30 and self.humedad > 70:
            self.accion = "Encender aire acondicionado (Modo Deshumidificador)"
        elif self.temperatura > 30:
            self.accion = "Encender ventilador"
        elif self.temperatura < 18:
            self.accion = "Encender calefacción"
        else:
            self.accion = "Mantener sistema apagado"
            
        return self.accion

# --- 3. Funciones de la Interfaz ---
def analizar_y_guardar():
    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada inválida", "Por favor, ingresa números válidos.")
        return

    agente = AgenteClimatizacion()
    decision = agente.tomar_decision(temp, hum)
    
    lbl_decision.config(text=f"Acción del Agente: {decision}", fg="blue")

    try:
        cliente = MongoClient(mongo_url)
        # Apuntamos a la colección que dicta el archivo .env
        coleccion = cliente[bd_nombre][coleccion_nombre] 
        
        nuevo_registro = {
            "temperatura_C": temp,
            "humedad_pct": hum,
            "accion_tomada": decision,
            "tipo_registro": "clima" # Agregamos esto para diferenciarlo de los animales
        }
        
        coleccion.insert_one(nuevo_registro)
        messagebox.showinfo("Éxito", f"¡Guardado en la colección '{coleccion_nombre}'!")
        
        entry_temp.delete(0, tk.END)
        entry_hum.delete(0, tk.END)
        cargar_historial()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

def cargar_historial():
    try:
        cliente = MongoClient(mongo_url)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        # Opcional: Solo traer los que sean de clima para no revolver la tabla
        # Si quieres ver todo (animales y clima), quita el filtro {"tipo_registro": "clima"}
        documentos = list(coleccion.find({"tipo_registro": "clima"}, {"_id": 0}))
        
        for item in tabla.get_children():
            tabla.delete(item)
            
        if not documentos:
            return
            
        for doc in documentos:
            valores = (doc.get("temperatura_C", ""), doc.get("humedad_pct", ""), doc.get("accion_tomada", ""))
            tabla.insert("", "end", values=valores)
            
    except Exception as e:
        print("Error al cargar:", e)

# --- 4. Configuración de la Ventana (Tkinter) ---
ventana = tk.Tk()
ventana.title("Agente de Climatización - Pruebas Atlas")
ventana.geometry("650x500")

marco_percepcion = tk.LabelFrame(ventana, text="Sensores (Percepción)", padx=10, pady=10)
marco_percepcion.pack(fill="x", padx=20, pady=10)

tk.Label(marco_percepcion, text="Temperatura (°C):").grid(row=0, column=0, padx=5, pady=5)
entry_temp = tk.Entry(marco_percepcion, width=10)
entry_temp.grid(row=0, column=1, padx=5, pady=5)

tk.Label(marco_percepcion, text="Humedad (%):").grid(row=0, column=2, padx=5, pady=5)
entry_hum = tk.Entry(marco_percepcion, width=10)
entry_hum.grid(row=0, column=3, padx=5, pady=5)

btn_analizar = tk.Button(marco_percepcion, text="Analizar y Guardar", command=analizar_y_guardar, bg="lightgreen")
btn_analizar.grid(row=0, column=4, padx=15, pady=5)

lbl_decision = tk.Label(ventana, text="Acción del Agente: Esperando datos...", font=("Arial", 11, "bold"))
lbl_decision.pack(pady=10)

tk.Label(ventana, text=f"Historial en la colección de pruebas:").pack(anchor="w", padx=20)

marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=5)

columnas = ("Temperatura", "Humedad", "Acción Tomada")
tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=150, anchor="center")

tabla.column("Acción Tomada", width=300, anchor="w")
tabla.pack(expand=True, fill="both")

cargar_historial()
ventana.mainloop()