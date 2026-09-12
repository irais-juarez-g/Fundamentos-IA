# Sistema de evaluación de alumnos
# Ejemplo de lógica proposicional

print("====================================")
print(" SISTEMA DE EVALUACIÓN DEL ALUMNO")
print("====================================")

# Entrada de información
asistencia = float(input("Ingresa el porcentaje de asistencia: "))
promedio = float(input("Ingresa el promedio del alumno: "))

proyecto = input("¿Entregó el proyecto? (si/no): ").lower()

# Proposiciones
P = asistencia >= 80
Q = promedio >= 8
R = proyecto == "si"

# Mostrar el valor de cada proposición
print("\n--- Evaluación de proposiciones ---")
print("P - Asistencia suficiente:", P)
print("Q - Promedio aprobatorio:", Q)
print("R - Proyecto entregado:", R)

# Aplicación de la lógica proposicional
resultado = P and Q and R

print("\n--- Resultado final ---")

if resultado:
    print("El alumno PUEDE presentar el examen final.")
else:
    print("El alumno NO puede presentar el examen final.")