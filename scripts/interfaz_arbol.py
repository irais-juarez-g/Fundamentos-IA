import tkinter as tk
from tkinter import messagebox, scrolledtext
from collections import deque

def encontrar_todas_las_rutas(grafo, inicio, fin, camino=[]):
    """Función para encontrar todas las rutas posibles sin ciclos."""
    camino = camino + [inicio]
    if inicio == fin:
        return [camino]
    if inicio not in grafo:
        return []
    
    rutas = []
    for nodo in grafo[inicio]:
        if nodo not in camino:
            nuevas_rutas = encontrar_todas_las_rutas(grafo, nodo, fin, camino)
            for nueva_ruta in nuevas_rutas:
                rutas.append(nueva_ruta)
    return rutas

class AppBusquedaArbolDinamico:
    def __init__(self, root):
        self.root = root
        self.root.title("Buscador Dinámico de Rutas - Árbol Raíz Variable")
        self.root.geometry("850x700")
        self.root.config(bg="#f4f6f9")

        # Definición del grafo base
        self.grafo = {
            'A': ['B', 'C'],
            'B': ['A', 'D'],
            'C': ['A', 'E'],
            'D': ['B'],
            'E': ['C', 'F'],
            'F': ['E']
        }

        # --- Interfaz Gráfica ---
        titulo = tk.Label(root, text="Buscador Interactivo con Árbol Dinámico", font=("Arial", 14, "bold"), bg="#f4f6f9", fg="#333")
        titulo.pack(pady=10)

        # Marco para entradas del usuario
        frame_entradas = tk.Frame(root, bg="#f4f6f9")
        frame_entradas.pack(pady=5)

        tk.Label(frame_entradas, text="Nodo Inicial (Raíz):", font=("Arial", 11, "bold"), bg="#f4f6f9").grid(row=0, column=0, padx=5)
        self.entry_inicio = tk.Entry(frame_entradas, font=("Arial", 11), width=5, justify="center")
        self.entry_inicio.grid(row=0, column=1, padx=5)
        self.entry_inicio.insert(0, "A")

        tk.Label(frame_entradas, text="Nodo Destino:", font=("Arial", 11, "bold"), bg="#f4f6f9").grid(row=0, column=2, padx=5)
        self.entry_fin = tk.Entry(frame_entradas, font=("Arial", 11), width=5, justify="center")
        self.entry_fin.grid(row=0, column=3, padx=5)
        self.entry_fin.insert(0, "F")

        self.btn_calcular = tk.Button(frame_entradas, text="Buscar y Reestructurar Árbol", font=("Arial", 11, "bold"), 
                                      bg="#2196F3", fg="white", padx=10, pady=2, command=self.ejecutar_busqueda)
        self.btn_calcular.grid(row=0, column=4, padx=15)

        # Resultados de texto
        frame_resultados = tk.Frame(root, bg="#f4f6f9")
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.txt_resultados = scrolledtext.ScrolledText(frame_resultados, width=95, height=8, font=("Consolas", 10))
        self.txt_resultados.pack(pady=5)

        # Lienzo (Canvas) para el árbol dinámico
        self.canvas_label = tk.Label(root, text="Árbol Reorganizado (El nodo inicial seleccionado aparece arriba):", font=("Arial", 10, "italic"), bg="#f4f6f9")
        self.canvas_label.pack(anchor="w", padx=15)

        self.canvas = tk.Canvas(root, width=810, height=280, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(padx=15, pady=10)

        # Dibujo inicial por defecto con raíz en A
        self.actualizar_visualizacion("A", [])

    def ejecutar_busqueda(self):
        inicio = self.entry_inicio.get().strip().upper()
        fin = self.entry_fin.get().strip().upper()

        if not inicio or not fin:
            messagebox.showerror("Error", "Por favor ingresa ambos nodos.")
            return

        if inicio not in self.grafo or fin not in self.grafo:
            messagebox.showerror("Error", f"Nodos inválidos. Deben estar entre: {list(self.grafo.keys())}")
            return

        # Encontrar todas las rutas
        todas_las_rutas = encontrar_todas_las_rutas(self.grafo, inicio, fin)
        
        self.txt_resultados.delete(1.0, tk.END)

        if not todas_las_rutas:
            self.txt_resultados.insert(tk.END, f"No se encontraron rutas desde '{inicio}' hasta '{fin}'.\n")
            self.actualizar_visualizacion(inicio, [])
            return

        # Encontrar la mejor ruta
        mejor_ruta = min(todas_las_rutas, key=len)

        # Mostrar resultados
        output = f"=== TODAS LAS RUTAS DESDE '{inicio}' HASTA '{fin}' ===\n"
        for i, ruta in enumerate(todas_las_rutas, 1):
            output += f"Ruta {i}: {' -> '.join(ruta)}\n"
        
        output += f"\n=== MEJOR RUTA (MÁS CORTA) ===\n"
        output += f"{' -> '.join(mejor_ruta)} (Total de pasos: {len(mejor_ruta) - 1})\n"
        
        self.txt_resultados.insert(tk.END, output)

        # Actualizar gráfico poniendo al nodo 'inicio' arriba
        self.actualizar_visualizacion(inicio, mejor_ruta)

    def construir_jerarquia_dinamica(self, raiz):
        """Construye niveles y relaciones padre-hijo basadas en el nodo que el usuario elija como raíz."""
        niveles = {}
        padres = {}
        visitados = {raiz}
        cola = deque([(raiz, 0)])
        
        niveles[0] = [raiz]

        while cola:
            nodo_actual, nivel = cola.popleft()
            
            for vecino in self.grafo[nodo_actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    padres[vecino] = nodo_actual
                    siguiente_nivel = nivel + 1
                    if siguiente_nivel not in niveles:
                        niveles[siguiente_nivel] = []
                    niveles[siguiente_nivel].append(vecino)
                    cola.append((vecino, siguiente_nivel))
                    
        return niveles, padres

    def actualizar_visualizacion(self, raiz, mejor_ruta):
        self.canvas.delete("all")
        
        niveles, padres = self.construir_jerarquia_dinamica(raiz)
        coordenadas = {}
        
        # Calcular coordenadas dinámicamente según la cantidad de niveles y nodos por nivel
        total_niveles = len(niveles)
        altura_canvas = 280
        ancho_canvas = 810
        
        espacio_y = altura_canvas / (total_niveles + 1)

        for nivel, nodos in niveles.items():
            y = (nivel + 1) * espacio_y
            total_en_nivel = len(nodos)
            espacio_x = ancho_canvas / (total_en_nivel + 1)
            
            for i, nodo in enumerate(nodos):
                x = (i + 1) * espacio_x
                coordenadas[nodo] = (x, y)

        # Dibujar líneas de conexión padre -> hijo
        for hijo, padre in padres.items():
            if padre in coordenadas and hijo in coordenadas:
                x1, y1 = coordenadas[padre]
                x2, y2 = coordenadas[hijo]
                
                # Comprobar si la arista pertenece a la mejor ruta
                es_optima = False
                for k in range(len(mejor_ruta) - 1):
                    if (mejor_ruta[k] == padre and mejor_ruta[k+1] == hijo) or (mejor_ruta[k] == hijo and mejor_ruta[k+1] == padre):
                        es_optima = True
                        break
                
                if es_optima:
                    self.canvas.create_line(x1, y1, x2, y2, width=4, fill="#4CAF50")
                else:
                    self.canvas.create_line(x1, y1, x2, y2, width=2, fill="#b0bec5")

        # Dibujar los nodos en el lienzo
        radio = 20
        for nodo, (x, y) in coordenadas.items():
            if nodo in mejor_ruta or nodo == raiz:
                color_relleno = "#C8E6C9" if nodo in mejor_ruta else "#FFF9C4"
                color_borde = "#2E7D32" if nodo in mejor_ruta else "#F57F17"
                ancho_borde = 3
            else:
                color_relleno = "#E3F2FD"
                color_borde = "#1565C0"
                ancho_borde = 2

            self.canvas.create_oval(x - radio, y - radio, x + radio, y + radio, 
                                    fill=color_relleno, outline=color_borde, width=ancho_borde)
            self.canvas.create_text(x, y, text=nodo, font=("Arial", 11, "bold"), fill="#000")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppBusquedaArbolDinamico(root)
    root.mainloop()