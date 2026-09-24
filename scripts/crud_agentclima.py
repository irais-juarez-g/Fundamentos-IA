import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

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

# --- 3. Funciones del CRUD ---

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
    """CREATE: Inserta un nuevo registro de clima"""
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

def cargar_historial(filtro_temp=None):
    """READ: Carga el historial desde MongoDB y guarda el ID en los tags de la tabla"""
    try:
        cliente = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        query = {"tipo_registro": "clima"}
        
        if filtro_temp is not None and filtro_temp != "":
            try:
                query["temperatura_C"] = float(filtro_temp)
            except ValueError:
                pass 
        
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
            
            # Guardamos el ID de MongoDB directamente en los tags de la fila
            tabla.insert("", "end", values=(temp, hum, accion), tags=(doc_id,))
            
    except Exception as e:
        print("Error al cargar el historial:", e)

def al_seleccionar_elemento(event):
    """Permite seleccionar un elemento de la tabla y extraer su ID oculto en los tags"""
    global id_seleccionado
    seleccion = tabla.selection()
    if not seleccion:
        return
    
    item = seleccion[0]
    tags = tabla.item(item, "tags")
    
    if tags:
        id_seleccionado = tags[0]  # Recuperamos el _id de MongoDB guardado en los tags
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
    """UPDATE: Modifica el registro seleccionado"""
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
    """DELETE: Elimina el registro seleccionado"""
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
    """QUERY: Busca por temperatura exacta"""
    criterio = entry_buscar.get().strip()
    cargar_historial(filtro_temp=criterio)

def limpiar_busqueda():
    entry_buscar.delete(0, tk.END)
    cargar_historial()

# --- 4. Configuración de la Ventana (Tkinter) ---
ventana = tk.Tk()
ventana.title("CRUD Agente de Climatización - Atlas")
ventana.geometry("700x550")

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

# Botones de Operaciones
btn_insertar = tk.Button(ventana, text="Insertar Nuevo", command=insertar_registro, bg="lightgreen", width=18)
btn_insertar.pack(side="top", padx=20, pady=2)

btn_actualizar = tk.Button(ventana, text="Actualizar Seleccionado", command=actualizar_registro, bg="lightblue", width=18)
btn_actualizar.pack(side="top", padx=20, pady=2)

btn_eliminar = tk.Button(ventana, text="Eliminar Seleccionado", command=eliminar_registro, bg="lightcoral", width=18)
btn_eliminar.pack(side="top", padx=20, pady=2)

btn_limpiar = tk.Button(ventana, text="Limpiar Cajas", command=limpiar_campos, width=18)
btn_limpiar.pack(side="top", padx=20, pady=2)

# Marco de Búsqueda / Consulta
marco_busqueda = tk.LabelFrame(ventana, text="Consultas / Búsqueda en Base de Datos", padx=10, pady=5)
marco_busqueda.pack(fill="x", padx=20, pady=5)

tk.Label(marco_busqueda, text="Filtrar por Temp (°C):").pack(side="left", padx=5)
entry_buscar = tk.Entry(marco_busqueda, width=12)
entry_buscar.pack(side="left", padx=5)

btn_buscar = tk.Button(marco_busqueda, text="Buscar", command=buscar_datos, bg="lightyellow")
btn_buscar.pack(side="left", padx=5)

btn_mostrar_todo = tk.Button(marco_busqueda, text="Mostrar Todos", command=limpiar_busqueda)
btn_mostrar_todo.pack(side="left", padx=5)

# Historial y Tabla
marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=5)

columnas = ("Temp (°C)", "Humedad (%)", "Acción del Agente")
tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", selectmode="browse")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, width=120, anchor="center")

tabla.column("Acción del Agente", width=300, anchor="w")
tabla.pack(side="left", expand=True, fill="both")

scrollbar = ttk.Scrollbar(marco_tabla, orient="vertical", command=tabla.yview)
scrollbar.pack(side="right", fill="y")
tabla.configure(yscrollcommand=scrollbar.set)

tabla.bind("<<TreeviewSelect>>", al_seleccionar_elemento)

# Cargar datos iniciales
cargar_historial()

ventana.mainloop()