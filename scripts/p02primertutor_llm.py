# ============================================================
# PRACTICA 2 - MODIFICADA
# ASISTENTE DE COCINA INTELIGENTE CON LLM Y TKINTER
# ============================================================

import tkinter as tk
from tkinter import scrolledtext, messagebox
import ollama

# ------------------------------------------------------------
# 1. CONFIGURACIÓN DEL MODELO
# ------------------------------------------------------------
MODELO = "llama3.2:1b"


# ------------------------------------------------------------
# 2. CONFIGURACIÓN DEL SISTEMA (ASISTENTE DE COCINA)
# ------------------------------------------------------------
mensaje_sistema = """
Eres un chef profesional y asistente de cocina experto.

Tu función es ayudar a entusiastas culinarios, estudiantes de gastronomía y cocineros caseros.

Debes:
1. Explicar técnicas culinarias, recetas y sustituciones de ingredientes de manera clara.
2. Utilizar pasos sencillos y ordenados.
3. Sugerir medidas, tiempos de cocción y consejos de seguridad alimentaria.
4. Adaptar el lenguaje para que sea accesible, amigable y práctico.
5. Cuando sea posible, sugerir variantes de recetas o maridajes.
6. Si el usuario comete un error en una receta o técnica, explicarle amablemente cómo corregirlo.
7. Explicar el fundamento científico o tradicional detrás de los procesos de cocina (ej. reacciones químicas, temperaturas).
"""

# Inicializar historial de mensajes
mensajes = [
    {
        "role": "system",
        "content": mensaje_sistema
    }
]


# ------------------------------------------------------------
# 3. INTERFAZ GRÁFICA CON TKINTER
# ------------------------------------------------------------
class AsistenteCocinaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chef IA - Asistente de Cocina Inteligente")
        self.root.geometry("700x600")
        self.root.minsize(500, 400)

        # Configuración de colores estilo cocina moderna (Tonos cálidos/crema y acentos oscuros)
        bg_color = "#f9f6f0"
        panel_color = "#ffffff"
        btn_color = "#d90696"  # Tono anaranjado tipo chef
        
        self.root.configure(bg=bg_color)

        # --- Título Superior ---
        titulo_label = tk.Label(
            self.root, 
            text="🍳 Chef IA: Tu Asistente Culinario Personal", 
            font=("Helvetica", 14, "bold"),
            bg=bg_color,
            fg="#1f2937"
        )
        titulo_label.pack(pady=10)

        # --- Cuadro de Texto para el Chat (Área de Conversación) ---
        self.chat_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            state=tk.DISABLED, 
            font=("Arial", 11),
            bg=panel_color,
            fg="#1f2937",
            padx=10,
            pady=10
        )
        self.chat_area.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

        # Configurar etiquetas de estilo para el chat
        self.chat_area.tag_config("usuario", foreground="#1d4ed8", font=("Arial", 11, "bold"))
        self.chat_area.tag_config("asistente", foreground="#047857", font=("Arial", 11))
        self.chat_area.tag_config("sistema", foreground="#6b7280", font=("Arial", 10, "italic"))

        # Mensaje de bienvenida inicial en el chat
        self._mostrar_en_chat("Sistema: ¡Hola! Soy tu chef virtual. Pregúntame sobre recetas, técnicas, sustituciones o maridajes.\n\n", "sistema")

        # --- Panel Inferior para Controles y Entrada ---
        inferior_frame = tk.Frame(self.root, bg=bg_color)
        inferior_frame.pack(padx=15, pady=10, fill=tk.X)

        # Campo de entrada de texto para el mensaje del usuario
        self.entrada_texto = tk.Entry(
            inferior_frame, 
            font=("Arial", 12),
            bg=panel_color,
            fg="#1f2937",
            relief=tk.SOLID,
            bd=1
        )
        self.entrada_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        # Permitir enviar presionando la tecla "Enter"
        self.entrada_texto.bind("<Return>", lambda event: self.enviar_mensaje())

        # Botón de Enviar
        self.btn_enviar = tk.Button(
            inferior_frame, 
            text="Enviar", 
            command=self.enviar_mensaje,
            font=("Arial", 10, "bold"),
            bg=btn_color,
            fg="white",
            relief=tk.RAISED,
            padx=20,
            pady=5
        )
        self.btn_enviar.pack(side=tk.RIGHT)

    def _mostrar_en_chat(self, texto, tag):
        """Método auxiliar para insertar texto en el área de chat de forma segura."""
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, texto, tag)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def enviar_mensaje(self):
        """Procesa la entrada del usuario, llama a Ollama y actualiza la interfaz."""
        pregunta = self.entrada_texto.get().strip()
        
        if not pregunta:
            return

        # Limpiar el campo de entrada inmediatamente
        self.entrada_texto.delete(0, tk.END)

        if pregunta.lower() == "salir":
            self.root.quit()
            return

        # Mostrar la pregunta del usuario en la interfaz
        self._mostrar_en_chat(f"Tú: {pregunta}\n", "usuario")

        # Agregar pregunta al arreglo de historial
        mensajes.append({
            "role": "user",
            "content": pregunta
        })

        # Realizar la consulta a Ollama dentro de un bloque try-except
        try:
            self._mostrar_en_chat("Chef IA está cocinando la respuesta...\n", "sistema")
            self.root.update_idletasks()

            respuesta = ollama.chat(
                model=MODELO,
                messages=mensajes
            )

            contenido = respuesta["message"]["content"]
            
            # Agregar respuesta al historial
            mensajes.append({
                "role": "assistant",
                "content": contenido
            })

            # Mostrar respuesta del asistente en la interfaz
            self._mostrar_en_chat(f"Chef IA:\n{contenido}\n\n" + "-"*40 + "\n", "asistente")

        except Exception as error:
            # Manejo de errores de conexión con Ollama
            mensaje_error = f"\n[ERROR: No se pudo conectar con Ollama. Verifica que esté ejecutándose. Detalle: {error}]\n"
            self._mostrar_en_chat(mensaje_error, "sistema")
            messagebox.showerror("Error de Conexión", f"No se pudo comunicar con el modelo LLM:\n{error}")
            
            # Revertir la última pregunta agregada ya que falló
            mensajes.pop()


# ------------------------------------------------------------
# 4. EJECUCIÓN PRINCIPAL DE LA APLICACIÓN
# ------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AsistenteCocinaApp(root)
    root.mainloop()