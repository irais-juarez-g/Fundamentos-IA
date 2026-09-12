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
print("BIENVENIDO DIAGNOSTICO MEDICO")
print("= *")
print("\n= Datos del paciente")
nombre = input("ingresa tu nombre: ")
edad = input("ingresa tu edad: ")
genero = input("ingresa tu genero: ")
peso = input("ingresa tu peso: ")
estatura = input("ingresa tu estatura ")
direccion = input("ingresa tu direccion: ")


# ============================================
# SISTEMA EXPERTO DE DIAGNÓSTICO
# ============================================

print("DIAGNÓSTICO")

fiebre = input("¿Tiene fiebre? (s/n): ")
tos = input("¿Tiene tos? (s/n): ")
dolor = input("¿Tiene dolor de garganta? (s/n): ")
estornudos = input("¿Tiene estornudos, flujo nasal? (s/n): ")
cuerpo_cortado = input("¿Tiene dolor muscular o cuerpo cortado? (s/n): ")
respirar = input("¿Tiene dificultad para respirar o falta de aire? (s/n): ")
dolor_pecho = input("¿Siente dolor o presion continua en el pecho? (s/n): ")


if fiebre == "s" and tos == "s" and estornudos == "s":

    diagnostico = "Posible infección respiratoria"

elif tos == "s" and dolor == "s" and cuerpo_cortado == "s":

    diagnostico = "Posible irritación respiratoria"

elif fiebre == "s" and dolor_pecho == "s":

    diagnostico = "Se recomienda valoración profesional"

elif tos or dolor or estornudos: 
    
    diagnostico = "Sistomatologia leve. Guardar reposo y mantener hidratacion"

else:

    diagnostico = "No se identificó un patrón"

print("\nResultado:")
print(diagnostico)


#Implementación de mejores decisiones para un mejor resultado.