# menu.py
# Las pantallas de menú e instrucciones, y el manejo del volumen.

from fantasma import dibujar_simbolo
from ajustes import (ANCHO, PASO_VOLUMEN, COLOR_TEXTO, COLOR_ELEGIDO,
                     COLOR_APAGADO)

OPCIONES = ["Jugar", "Instrucciones", "Volumen", "Salir"]


def escribir(pantalla, fuente, texto, color, centro):
    """Escribe un texto centrado en el punto que se le pasa."""
    sup = fuente.render(texto, True, color)
    rect = sup.get_rect(center=centro)
    pantalla.blit(sup, rect)


def cambiar_volumen(volumen, cambio):
    """Devuelve el volumen nuevo, siempre entre 0 y 1."""
    nuevo = round(volumen + cambio * PASO_VOLUMEN, 1)
    if nuevo < 0:
        nuevo = 0
    if nuevo > 1:
        nuevo = 1
    return nuevo


def aplicar_volumen(sonidos, volumen):
    """Le pone el mismo volumen a todos los sonidos de la lista."""
    for s in sonidos:
        s.set_volume(volumen)


def dibujar_menu(pantalla, fuente, fuente_grande, seleccion, volumen):
    escribir(pantalla, fuente_grande, "El gato mago", COLOR_TEXTO, (ANCHO // 2, 80))
    escribir(pantalla, fuente, "Dibujá en el aire para espantar fantasmas",
             COLOR_APAGADO, (ANCHO // 2, 125))

    for i in range(len(OPCIONES)):
        texto = OPCIONES[i]
        if texto == "Volumen":
            texto = f"< Volumen: {int(volumen * 100)}% >"
        if i == seleccion:
            color = COLOR_ELEGIDO
            texto = "> " + texto + " <"
        else:
            color = COLOR_APAGADO
        escribir(pantalla, fuente, texto, color, (ANCHO // 2, 200 + i * 50))

    escribir(pantalla, fuente, "Flechas para moverte, Enter para elegir, Esc para salir",
             COLOR_APAGADO, (ANCHO // 2, 440))


def dibujar_instrucciones(pantalla, fuente, fuente_grande):
    escribir(pantalla, fuente_grande, "Cómo se juega", COLOR_TEXTO, (ANCHO // 2, 50))

    lineas = [
        "Los fantasmas vienen a buscar al gato.",
        "Cada uno tiene un símbolo arriba de la cabeza.",
        "Juntá el índice y el pulgar y dibujá ese símbolo en el aire.",
        "Separá los dedos para lanzar el hechizo.",
        "Se van todos los fantasmas que tengan ese símbolo.",
        "Si uno toca al gato, perdés una vida. Tenés 3.",
        "Aguantá 3 oleadas para ganar.",
    ]
    for i in range(len(lineas)):
        escribir(pantalla, fuente, lineas[i], COLOR_TEXTO, (ANCHO // 2, 100 + i * 32))

    # los cuatro símbolos que existen
    simbolos = ["—", "|", "V", "Λ"]
    for i in range(len(simbolos)):
        x = ANCHO // 2 - 150 + i * 100
        dibujar_simbolo(pantalla, simbolos[i], x, 360, 20)

    escribir(pantalla, fuente, "Esc o Enter para volver al menú", COLOR_ELEGIDO, (ANCHO // 2, 440))