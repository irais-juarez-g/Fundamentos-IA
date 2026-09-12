# Definición de conectores lógicos
def negacion(p):
    return not p

def conjuncion(p, q):
    return p and q

def disyuncion(p, q):
    return p or q

def condicional(p, q):
    return (not p) or q

def bicondicional(p, q):
    return p == q

# Encabezado de la tabla
print(f"{'p':<5} | {'q':<5} | {'~p':<5} | {'p y q':<7} | {'p o q':<7} | {'p => q':<7} | {'p <=> q':<7}")
print("-" * 55)

# Combinaciones de valores de verdad (True / False)
valores = [True, False]

for p in valores:
    for q in valores:
        not_p = negacion(p)
        and_pq = conjuncion(p, q)
        or_pq = disyuncion(p, q)
        cond_pq = condicional(p, q)
        bicond_pq = bicondicional(p, q)
        
        print(f"{str(p):<5} | {str(q):<5} | {str(not_p):<5} | {str(and_pq):<7} | {str(or_pq):<7} | {str(cond_pq):<7} | {str(bicond_pq):<7}")