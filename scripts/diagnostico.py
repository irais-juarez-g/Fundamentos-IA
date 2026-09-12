import random
from datetime import datetime

#REPORTE
numero = random.randint(1000, 9999)

#identificador 
numero_reporte = "R" + str(numero)

#fecha y hora 
ahora = datetime.now()
fecha_hora = ahora.strftime("%Y-%m-%d %H:%M:%S")


#bienvenida
print("\n= *")
print("BIENVENIDO AL DIAGNOSTICO DEL EQUIPO")
print("= *")
print("\n= Datos del usuario")
nombre = input("ingresa tu nombre: ")
direccion = input("ingresa tu direccion: ")

print("\n= Tipo de dispositivo")
print("Op 1: PC")
print("Op 2: Laptop")
print("Op 3: Servidor")
print("Op 4: Tablet")
opcion = input("Selecciona una opción (1-4): ")

if opcion == "1":
    dispositivo = "PC"
elif opcion == "2":
    dispositivo = "Laptop"
elif opcion == "3":
    dispositivo = "Servidor"
elif opcion == "4":
    dispositivo = "Tablet"
else:
    print("Equipo 'Desconocido'.")
    dispositivo = "Desconocido"
    
#Diagnóstico
print("\n= Diagnóstico del equipo")

#funcion auxiliar para convertir respuesta a boleano
def responder(mensaje):
    res = input(mensaje).strip().lower()
    return res.startswith(('s', 'y'))


diagnostico_resultado = []

#bucle de evaluacion usando logica proposicional
ejecutando = True
while ejecutando:
    # Proposición p: ¿El equipo recibe energía / tiene electricidad?
    p = responder("¿El equipo tiene electricidad / recibe corriente? (s/n): ")
    
    if not p: # ~p => Falla de energía
        diagnostico_resultado = [
            "Falla de Alimentación / Energía (~p)",
            "- Revisar cargador, cable de corriente o tomacorriente.",
            "- Posible falla en el centro de carga o tarjeta madre (Power Delivery)."
        ]
        ejecutando = False
        break

    # Proposición q: ¿El equipo enciende al presionar el botón?
    q = responder("¿El equipo enciende (luces/ventiladores)? (s/n): ")
    
    if not q: # p AND ~q => Falla de encendido
        diagnostico_resultado = [
            "Falla de Encendido (p ∧ ~q)",
            "- Batería completamente agotada o dañada.",
            "- Falla en el botón de encendido o flex de interconexión.",
            "- Daño en circuito primario de la tarjeta madre."
        ]
        ejecutando = False
        break

    # Proposición r: ¿Muestra imagen en la pantalla?
    r = responder("¿Muestra imagen en la pantalla? (s/n): ")
    
    if not r: # (p AND q) AND ~r => Falla de video
        diagnostico_resultado = [
            "Falla de Video / Pantalla",
            "- Falla en la pantalla o cable flex de video.",
            "- Falla o suciedad en módulos de memoria RAM.",
            "- Falla en chip gráfico (GPU) o procesador."
        ]
        ejecutando = False
        break

    # Proposiciones secundarias si el equipo enciende y da imagen (p AND q AND r)
    s = responder("¿El equipo se sobrecalienta o hace ruidos extraños? (s/n): ")
    t = responder("¿Recibió algún golpe físico reciente? (s/n): ")
    u = responder("¿La batería o puertos periféricos presentan fallas? (s/n): ")

    diagnostico_resultado.append("Evaluación General del Sistema (p ∧ q ∧ r):")
    
    if s:
        diagnostico_resultado.append("- Requiere mantenimiento preventivo (limpieza interna / pasta térmica).")
    if t:
        diagnostico_resultado.append("- Revisión de estructura física y estado de disco duro mecánico.")
    if u:
        diagnostico_resultado.append("- Reemplazo de batería por ciclo consumido o revisión de puertos USB/Wi-Fi.")
    if not (s or t or u):
        diagnostico_resultado.append("- Hardware operando correctamente. Posible problema a nivel software/SO.")

ejecutando = False

# ===================================================
# IMPRESIÓN Y EXPORTACIÓN DEL REPORTE
# ===================================================
lineas_reporte = [
    "="*40,
    f"REPORTE DE DIAGNÓSTICO: {numero_reporte}",
    f"Fecha y Hora: {fecha_hora}",
    f"Cliente: {nombre}",
    f"Dirección: {direccion}",
    f"Dispositivo: {dispositivo}",
    "="*40,
    "RESULTADO DEL DIAGNÓSTICO:"
] + diagnostico_resultado + ["="*40]

# Mostrar en consola
print("\n")
for linea in lineas_reporte:
    print(linea)

# Guardar en archivo TXT
nombre_archivo = f"reporte_{numero_reporte}.txt"
with open(nombre_archivo, "w", encoding="utf-8") as f:
    for linea in lineas_reporte:
        f.write(linea + "\n")

print(f"\n¡Reporte guardado con éxito como '{nombre_archivo}'!")