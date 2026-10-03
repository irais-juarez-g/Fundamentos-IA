def encontrar_todas_las_rutas(grafo, inicio, fin, camino=[]):
    """Función recursiva para encontrar todas las rutas posibles sin ciclos."""
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

# Definición del grafo basado en los estados de la pizarra:
# A = (B, C), B = (A, D), C = (A, E), D = (B), E = (C, F), F = (E)
grafo = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'E'],
    'D': ['B'],
    'E': ['C', 'F'],
    'F': ['E']
}

inicio = 'A'
fin = 'F'

# Obtener todas las rutas posibles hasta F
todas_las_rutas = encontrar_todas_las_rutas(grafo, inicio, fin)

print("=== TODAS LAS RUTAS POSIBLES HASTA F ===")
for i, ruta in enumerate(todas_las_rutas, 1):
    print(f"Ruta {i}: {' -> '.join(ruta)}")

# Encontrar la mejor ruta (la de menor longitud)
if todas_las_rutas:
    mejor_ruta = min(todas_las_rutas, key=len)
    print("\n=== LA MEJOR RUTA (MÁS CORTA) ===")
    print(f"{' -> '.join(mejor_ruta)} (Total de saltos/pasos: {len(mejor_ruta) - 1})")
else:
    print("No se encontró ninguna ruta hacia F.")