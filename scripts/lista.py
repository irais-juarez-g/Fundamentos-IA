from datetime import datetime
# ==========================================================
# REGISTRO DEL REPORTE
# ==========================================================

from uuid import uuid4

print("\n==========================================")
print("       BIENVENIDO AL SOPORTE TECNICO")
print("==========================================")

nombre = input("Nombre del usuario: ").strip()
direccion = input("Dirección del usuario: ").strip()

tipos_dispositivo = {
    "pc": "PC",
    "laptop": "Laptop",
    "servidor": "Servidor",
    "tablet": "Tablet",
}

while True:
    tipo_ingresado = input("Tipo de dispositivo (PC, laptop, servidor o tablet): ").strip().lower()
    if tipo_ingresado in tipos_dispositivo:
        tipo_dispositivo = tipos_dispositivo[tipo_ingresado]
        break
    print("Tipo no válido. Seleccione PC, laptop, servidor o tablet.")

def generar_numero_reporte():
    fecha = datetime.now().strftime("%Y%m%d-%H%M%S")
    identificador = uuid4().hex[:6].upper()
    return f"REP-{fecha}-{identificador}"


numero_reporte = generar_numero_reporte()

print("\n==========================================")
print("          REPORTE REGISTRADO")
print("==========================================")
print("N° de reporte:", numero_reporte)
print("Usuario:", nombre)
print("Dirección:", direccion)
print("Dispositivo:", tipo_dispositivo)


# ==========================================================
# EVALUACIÓN MEDIANTE LÓGICA PROPOSICIONAL
# ==========================================================

def respuesta_booleana(pregunta):
    """Convierte respuestas afirmativas que comienzan con s o y en True."""
    return input(pregunta).strip().lower().startswith(("s", "y"))


def eval_energia():
    return [
        "No se detecta corriente eléctrica.",
        "Revisar la conexión eléctrica, el cable y el contacto de energía.",
    ]


def eval_encendido(golpe):
    causas = [
        "Revisar la fuente de poder, el botón de encendido y las conexiones internas."
    ]
    if golpe:
        causas.insert(0, "El golpe físico puede haber dañado la fuente o componentes internos.")
    return causas


def eval_video(golpe):
    causas = [
        "Revisar la pantalla, la memoria RAM, la tarjeta gráfica y las conexiones de video."
    ]
    if golpe:
        causas.insert(0, "El golpe físico puede haber afectado la pantalla o sus conexiones.")
    return causas


def eval_sistema(s, t, u):
    causas = []
    if s:
        causas.append("Sobrecalentamiento o ruido: revisar ventiladores, disipador y disco.")
    if t:
        causas.append("Daño físico: realizar una revisión interna del equipo.")
    if u:
        causas.append("Falla de batería o periféricos: revisar cargador, conectores y controladores.")
    if not causas:
        causas.append("Funcionamiento básico correcto; no se detectaron fallas evidentes.")
    return causas


def diagnosticar(p, q, r, s, t, u):
    """Aplica las reglas jerárquicas y termina en la primera conclusión aplicable."""
    if not p:  # ¬p => EVAL_ENERGÍA y terminar
        return "EVAL_ENERGÍA", eval_energia()
    if p and not q:  # p ∧ ¬q => EVAL_ENCENDIDO y terminar
        return "EVAL_ENCENDIDO", eval_encendido(t)
    if p and q and not r:  # p ∧ q ∧ ¬r => EVAL_VIDEO y terminar
        return "EVAL_VIDEO", eval_video(t)
    return "DIAGNÓSTICO_SISTEMA", eval_sistema(s, t, u)  # p ∧ q ∧ r


# ==========================================================
# CAPTURA Y REPORTE FINAL
# ==========================================================

modelo = input("¿Cuál es el modelo de la computadora?: ").strip()
p = respuesta_booleana("¿El equipo tiene electricidad o recibe corriente? (s/n): ")
q = respuesta_booleana("¿El equipo enciende? (s/n): ")
r = respuesta_booleana("¿El equipo muestra imagen en pantalla? (s/n): ")
t = respuesta_booleana("¿El equipo recibió un golpe físico reciente? (s/n): ")
s = respuesta_booleana("¿El equipo se sobrecalienta o presenta ruidos extraños? (s/n): ")
u = respuesta_booleana("¿La batería o los periféricos presentan fallas? (s/n): ")
version = input("¿Qué versión del sistema utiliza?: ").strip()

modulo, causas = diagnosticar(p, q, r, s, t, u)
proposiciones = {"p": p, "q": q, "r": r, "s": s, "t": t, "u": u}

print("\n==========================================")
print("             DIAGNÓSTICO FINAL")
print("==========================================")
print("N° de reporte:", numero_reporte)
print("Modelo:", modelo)
print("Sistema:", version)
print("Módulo ejecutado:", modulo)
print("Proposiciones verdaderas:", ", ".join(letra for letra, valor in proposiciones.items() if valor) or "Ninguna")
print("Causas probables:")
for causa in causas:
    print("-", causa)

print("\n")
print("          FIN DEL DIAGNÓSTICO")
print("")