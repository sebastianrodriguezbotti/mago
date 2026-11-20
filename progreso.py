# progreso.py
# Guarda en un archivo cuántos niveles están desbloqueados,
# así el progreso no se pierde al cerrar el juego.

import json
from ajustes import ARCHIVO_PROGRESO, NIVELES, DESBLOQUEAR_TODO


def cargar_progreso():
    """Devuelve cuántos niveles están desbloqueados (1 = solo el primero)."""
    if DESBLOQUEAR_TODO:
        return len(NIVELES)
    try:
        with open(ARCHIVO_PROGRESO, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        desbloqueados = int(datos["desbloqueados"])
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError):
        desbloqueados = 1    # si no hay archivo, o está roto, se empieza de cero
    return max(1, min(len(NIVELES), desbloqueados))


def guardar_progreso(desbloqueados):
    """Escribe en el archivo cuántos niveles están desbloqueados."""
    with open(ARCHIVO_PROGRESO, "w", encoding="utf-8") as archivo:
        json.dump({"desbloqueados": desbloqueados}, archivo)


def desbloquear(desbloqueados, nivel_completado):
    """Recibe cuántos había desbloqueados y el nivel recién completado (0 es el primero).
    Devuelve cuántos quedan desbloqueados, y si cambió lo guarda."""
    nuevo = min(len(NIVELES), max(desbloqueados, nivel_completado + 2))
    if nuevo != desbloqueados:
        guardar_progreso(nuevo)
    return nuevo