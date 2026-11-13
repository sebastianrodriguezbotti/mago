# hechizos.py
# Reconoce qué símbolo se dibujó a partir de la lista de puntos del trazo.
# Ojo: en la pantalla la y crece hacia ABAJO.

from ajustes import PUNTOS_MINIMOS, PROPORCION_LINEA


def reconocer_simbolo(puntos):
    """Recibe una lista de (x, y) y devuelve "—", "|", "V", "Λ" o None."""
    if len(puntos) < PUNTOS_MINIMOS:
        return None

    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    ancho = max(xs) - min(xs)
    alto = max(ys) - min(ys)

    if ancho > alto * PROPORCION_LINEA:
        return "—"
    if alto > ancho * PROPORCION_LINEA:
        return "|"

    primero = puntos[0]
    ultimo = puntos[-1]
    medio = puntos[len(puntos) // 2]

    if medio[1] > primero[1] and medio[1] > ultimo[1]:
        return "V"      # el medio está más abajo que las dos puntas
    if medio[1] < primero[1] and medio[1] < ultimo[1]:
        return "Λ"      # el medio está más arriba que las dos puntas
    return None