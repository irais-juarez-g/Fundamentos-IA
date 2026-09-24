import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
import matplotlib.pyplot as plt

# --- 1. Cargar Credenciales de la Base de Datos ---
load_dotenv()
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

# Construir URL de conexión
mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"

# Variable global para almacenar el ID del documento seleccionado
id_seleccionado = None

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

# --- 3. Funciones del CRUD y Gráficos ---

def limpiar_campos():
    global id_seleccionado
    id_seleccionado = None
    entry_temp.delete(0, tk.END)
    entry_hum.delete(0, tk.END)
    lbl_modo.config(text="Modo: INSERTANDO NUEVO", fg="green")
    if 'tabla' in globals():
        for item in tabla.selection():
            tabla.selection_remove(item)

def insertar_registro():
    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada inválida", "Por favor, ingresa números válidos para temperatura y humedad.")
        return

    agente = AgenteClimatizacion()
    decision = agente.tomar_decision(temp, hum)

    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre] 
        
        nuevo_registro = {
            "temperatura_C": temp,
            "humedad_pct": hum,
            "accion_tomada": decision,
            "tipo_registro": "clima"
        }
        
        coleccion.insert_one(nuevo_registro)
        messagebox.showinfo("Éxito", f"¡Registro guardado en la colección '{coleccion_nombre}'!")
        limpiar_campos()
        cargar_historial()
        
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo guardar en MongoDB:\n{e}")

def cargar_historial(filtro_temp=None, filtro_accion=None):
    """READ: Carga el historial aplicando filtros opcionales de temperatura o acción"""
    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        query = {"tipo_registro": "clima"}
        
        if filtro_temp is not None and filtro_temp != "":
            try:
                query["temperatura_C"] = float(filtro_temp)
            except ValueError:
                pass 
                
        if filtro_accion is not None and filtro_accion != "":
            query["accion_tomada"] = {"$regex": filtro_accion, "$options": "i"}
        
        documentos = list(coleccion.find(query))
        
        for item in tabla.get_children():
            tabla.delete(item)
            
        if not documentos:
            return
            
        for doc in documentos:
            doc_id = str(doc.get("_id"))
            temp = doc.get("temperatura_C", "")
            hum = doc.get("humedad_pct", "")
            accion = doc.get("accion_tomada", "")
            
            tabla.insert("", "end", values=(temp, hum, accion), tags=(doc_id,))
            
    except Exception as e:
        print("Error al cargar el historial:", e)

def al_seleccionar_elemento(event):
    global id_seleccionado
    seleccion = tabla.selection()
    if not seleccion:
        return
    
    item = seleccion[0]
    tags = tabla.item(item, "tags")
    
    if tags:
        id_seleccionado = tags[0]
    else:
        id_seleccionado = None
    
    valores = tabla.item(item, "values")
    if valores:
        entry_temp.delete(0, tk.END)
        entry_temp.insert(0, valores[0])
        
        entry_hum.delete(0, tk.END)
        entry_hum.insert(0, valores[1])
        
        lbl_modo.config(text=f"Modo: EDITANDO (ID activo)", fg="blue")

def actualizar_registro():
    global id_seleccionado
    if not id_seleccionado:
        messagebox.showwarning("Aviso", "Primero selecciona un registro de la tabla para editar.")
        return

    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada inválida", "Ingresa números válidos.")
        return

    agente = AgenteClimatizacion()
    nueva_decision = agente.tomar_decision(temp, hum)

    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        resultado = coleccion.update_one(
            {"_id": ObjectId(id_seleccionado)},
            {"$set": {
                "temperatura_C": temp,
                "humedad_pct": hum,
                "accion_tomada": nueva_decision
            }}
        )
        
        if resultado.modified_count > 0:
            messagebox.showinfo("Éxito", "Registro actualizado correctamente en MongoDB.")
        else:
            messagebox.showinfo("Aviso", "No se realizaron cambios (los datos eran idénticos).")
            
        limpiar_campos()
        cargar_historial()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar:\n{e}")

def eliminar_registro():
    global id_seleccionado
    if not id_seleccionado:
        messagebox.showwarning("Aviso", "Primero selecciona un registro de la tabla para eliminar.")
        return

    confirmacion = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este registro?")
    if not confirmacion:
        return

    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        coleccion.delete_one({"_id": ObjectId(id_seleccionado)})
        messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
        
        limpiar_campos()
        cargar_historial()
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

def buscar_datos():
    criterio = entry_buscar.get().strip()
    cargar_historial(filtro_temp=criterio)

def filtrar_accion(accion_texto):
    cargar_historial(filtro_accion=accion_texto)

def limpiar_busqueda():
    entry_buscar.delete(0, tk.END)
    cargar_historial()

def graficar_datos():
    """Genera una gráfica con Matplotlib (Eje X: Temperatura, Eje Y: Humedad)"""
    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        documentos = list(coleccion.find({"tipo_registro": "clima"}))
        
        if not documentos:
            messagebox.showwarning("Sin datos", "No hay registros en la base de datos para graficar.")
            return

        temperaturas = [doc.get("temperatura_C", 0) for doc in documentos]
        humedades = [doc.get("humedad_pct", 0) for doc in documentos]
        acciones = [doc.get("accion_tomada", "N/A") for doc in documentos]

        plt.figure(figsize=(8, 5))
        plt.scatter(temperaturas, humedades, color='teal', s=100, edgecolors='black', alpha=0.7)
        
        plt.title("Gráfica: Temperatura vs Humedad", fontsize=14)
        plt.xlabel("Temperatura (°C) [Eje X]", fontsize=12)
        plt.ylabel("Humedad (%) [Eje Y]", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)

        # Mostrar la gráfica interactiva de Matplotlib
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la gráfica:\n{e}")

# --- 4. Configuración de la Ventana (Tkinter) ---
ventana = tk.Tk()
ventana.title("CRUD Agente de Climatización - Atlas")
ventana.geometry("740x660")

# Marco de Sensores y Controles
marco_percepcion = tk.LabelFrame(ventana, text="Sensores", padx=10, pady=10)
marco_percepcion.pack(fill="x", padx=20, pady=10)

tk.Label(marco_percepcion, text="Temperatura (°C):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_temp = tk.Entry(marco_percepcion, width=10)
entry_temp.grid(row=0, column=1, padx=5, pady=5)

tk.Label(marco_percepcion, text="Humedad (%):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_hum = tk.Entry(marco_percepcion, width=10)
entry_hum.grid(row=0, column=3, padx=5, pady=5)

lbl_modo = tk.Label(marco_percepcion, text="Modo: INSERTANDO NUEVO", font=("Arial", 10, "bold"), fg="green")
lbl_modo.grid(row=0, column=4, padx=10, pady=5)

# Botones de Operaciones CRUD
btn_insertar = tk.Button(ventana, text="Insertar Nuevo", command=insertar_registro, bg="lightgreen", width=22)
btn_insertar.pack(side="top", padx=20, pady=2)

btn_actualizar = tk.Button(ventana, text="Actualizar Seleccionado", command=actualizar_registro, bg="lightblue", width=22)
btn_actualizar.pack(side="top", padx=20, pady=2)

btn_eliminar = tk.Button(ventana, text="Eliminar Seleccionado", command=eliminar_registro, bg="lightcoral", width=22)
btn_eliminar.pack(side="top", padx=20, pady=2)

btn_limpiar = tk.Button(ventana, text="Limpiar Cajas", command=limpiar_campos, width=22)
btn_limpiar.pack(side="top", padx=20, pady=2)

# Botón para Gráfica con Matplotlib
btn_graficar = tk.Button(ventana, text="📊 Graficar Registros", command=graficar_datos, bg="#ffd166", font=("Arial", 10, "bold"), width=22)
btn_graficar.pack(side="top", padx=20, pady=5)

# Marco de Búsqueda y Botones de Filtro por Acción
marco_busqueda = tk.LabelFrame(ventana, text="Consultas / Filtros por Acción", padx=10, pady=8)
marco_busqueda.pack(fill="x", padx=20, pady=5)

tk.Label(marco_busqueda, text="Temp:").pack(side="left", padx=2)
entry_buscar = tk.Entry(marco_busqueda, width=6)
entry_buscar.pack(side="left", padx=2)

btn_buscar = tk.Button(marco_busqueda, text="Buscar", command=buscar_datos, bg="lightyellow")
btn_buscar.pack(side="left", padx=4)

# Botones Encender / Mantener
btn_encender = tk.Button(marco_busqueda, text="Encender...", command=lambda: filtrar_accion("Encender"), bg="#ffadad")
btn_encender.pack(side="left", padx=4)

btn_mantener = tk.Button(marco_busqueda, text="Mantener", command=lambda: filtrar_accion("Mantener"), bg="#caffbf")
btn_mantener.pack(side="left", padx=4)

btn_mostrar_todo = tk.Button(marco_busqueda, text="Todos", command=limpiar_busqueda)
btn_mostrar_todo.pack(side="left", padx=4)

# Historial y Tabla
marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=5)

columnas = ("Temp (°C)", "Humedad (%)", "Acción del Agente")
tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", selectmode="browse")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=120, anchor="center")

tabla.column("Acción del Agente", width=320, anchor="w")
tabla.pack(side="left", expand=True, fill="both")

scrollbar = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
scrollbar.pack(side="right", fill="y")
tabla.configure(yscrollcommand=scrollbar.set)

tabla.bind("<<TreeviewSelect>>", al_seleccionar_elemento)

# Cargar datos iniciales
cargar_historial()

ventana.mainloop()