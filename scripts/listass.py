# ==========================================================
# SISTEMA DE AUTORIZACIÓN PARA EXAMEN
# ==========================================================

# 1. ENTRADAS DE DATOS (ACADÉMICOS Y HARDWARE)
# ----------------------------------------------------------
asistencia = float(input("Ingresa el porcentaje de asistencia (0-100): "))
promedio = float(input("Ingresa el promedio del alumno: "))
proyecto = input("¿Entregó el proyecto? (si/no): ").lower()
adeudos = input("¿Tiene adeudos? (si/no): ").lower()
autorizacion = input("¿Tiene autorización especial? (si/no): ").lower()
lista_oficial = input("¿Aparece en la lista oficial? (si/no): ").lower()


# 2. PROPOSICIONES Y DIAGNÓSTICO DE HARDWARE
# ----------------------------------------------------------
print("\n--- DATOS Y REVISIÓN DEL EQUIPO ---")
tipo_equipo = input("¿Tipo de equipo? (laptop/escritorio): ").lower()
so = input("¿Sistema operativo? (windows/mac/linux/otro): ").lower()
ram = int(input("¿Memoria RAM en GB?: "))

electricidad = (input("¿Tiene electricidad / batería? (si/no): ")).lower() == "si"

# Evitamos contradicciones evaluando en cascada
if not electricidad:
    enciende = False
    imagen = False
    print("Diagnóstico: Revisar la alimentación o carga.")
else:
    enciende = (input("¿Enciende? (si/no): ")).lower() == "si"
    if not enciende:
        imagen = False
        print("Diagnóstico: Revisar la fuente de poder.")
    else:
        imagen = (input("¿Tu equipo da imagen? (si/no): ")).lower() == "si"
        if not imagen:
            print("Diagnóstico: Revisar monitor o memoria RAM.")
        else:
            print("Diagnóstico: Funcionamiento básico correcto.")

# Diagnóstico de especificaciones
if ram < 8:
    print("Diagnóstico RAM: Memoria baja (mínimo 8 GB recomendados).")

# E = El equipo funciona y cumple con la RAM suficiente
E = electricidad and enciende and imagen and (ram >= 8)

# P = Tiene asistencia suficiente
P = asistencia >= 80

# Q = Tiene promedio aprobatorio
Q = promedio >= 7

# R = Entregó el proyecto
R = proyecto == "si"

# S = NO tiene adeudos
S = adeudos == "no"

# T = Tiene autorización especial
T = autorizacion == "si"

# U = Aparece en la lista oficial
U = lista_oficial == "si"


# ----------------------------------------------------------
# 3. MOSTRAR PROPOSICIONES
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("           PROPOSICIONES")
print("=" * 55)

print("E - Equipo apto (Hardware/RAM):", E)
print("P - Asistencia suficiente :", P)
print("Q - Promedio aprobatorio  :", Q)
print("R - Proyecto entregado    :", R)
print("S - Sin adeudos           :", S)
print("T - Autorización especial :", T)
print("U - Está en lista oficial :", U)


# ----------------------------------------------------------
# 4. NEGACIÓN
# ----------------------------------------------------------

no_U = not U

print("\nNEGACIÓN")
print("¬U - NO está en lista oficial:", no_U)


# ----------------------------------------------------------
# 5. CONJUNCIÓN
# ----------------------------------------------------------

conjuncion = P and Q

print("\nCONJUNCIÓN")
print("P ∧ Q =", conjuncion)


# ----------------------------------------------------------
# 6. DISYUNCIÓN
# ----------------------------------------------------------

disyuncion = Q or T

print("\nDISYUNCIÓN")
print("Q ∨ T =", disyuncion)


# ----------------------------------------------------------
# 7. CONDICIONAL
# ----------------------------------------------------------

# P → Q
# (NOT P) OR Q

condicional = (not P) or Q

print("\nCONDICIONAL")
print("P → Q =", condicional)


# ----------------------------------------------------------
# 8. BICONDICIONAL
# ----------------------------------------------------------

# T ↔ U
bicondicional = T == U

print("\nBICONDICIONAL")
print("T ↔ U =", bicondicional)


# ----------------------------------------------------------
# 9. REGLA PRINCIPAL
# ----------------------------------------------------------

# El alumno DEBE estar en la lista oficial (U) y su equipo DEBE ser apto (E).
# Expresión completa:
# (U AND E) AND ((P AND Q AND R AND S) OR T)

resultado = (U and E) and ((P and Q and R and S) or T)


# ----------------------------------------------------------
# 10. DECISIÓN FINAL
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("                RESULTADO")
print("=" * 55)

if not U:
    print("El alumno NO aparece en la lista oficial.")
    print("NO PUEDE PRESENTAR EL EXAMEN.")

elif not E:
    print("El alumno aparece en lista, pero el equipo NO cumple los requisitos técnicos.")
    print("NO PUEDE PRESENTAR EL EXAMEN.")

elif resultado:
    print("El alumno y su equipo cumplen los requisitos.")
    print("PUEDE PRESENTAR EL EXAMEN.")

else:
    print("El alumno aparece en la lista oficial,")
    print("pero NO cumple los demás requisitos.")
    print("NO PUEDE PRESENTAR EL EXAMEN.")