# historia.py
# La introducción que se cuenta antes del nivel 1: páginas de texto que aparecen
# letra por letra, como si alguien las estuviera escribiendo.

import pygame
import menu
from ajustes import ANCHO, ALTO, HISTORIA_INICIO, CUADROS_POR_LETRA, BLANCO, PLATA


def texto_visible(texto, cuadros):
    """Devuelve la parte del texto que ya apareció, según cuántos cuadros pasaron."""
    letras = cuadros // CUADROS_POR_LETRA
    return texto[:letras]


def pagina_completa(pagina, cuadros):
    """Devuelve True si ya apareció todo el texto de la página."""
    return len(texto_visible(HISTORIA_INICIO[pagina], cuadros)) >= len(HISTORIA_INICIO[pagina])


def evento_historia(e, pagina, cuadros):
    """Recibe un evento en la introducción. Enter o clic: si la página se está escribiendo,
    la completa; si ya está completa, pasa a la siguiente. Esc saltea toda la historia.
    Devuelve (pagina, cuadros, termino): termino es True cuando hay que empezar a jugar."""
    avanzar = False
    if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            return pagina, cuadros, True
        if e.key in (pygame.K_RETURN, pygame.K_SPACE):
            avanzar = True
    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        avanzar = True

    if avanzar:
        if not pagina_completa(pagina, cuadros):
            cuadros = len(HISTORIA_INICIO[pagina]) * CUADROS_POR_LETRA    # mostrar todo ya
        elif pagina == len(HISTORIA_INICIO) - 1:
            return pagina, cuadros, True
        else:
            pagina += 1
            cuadros = 0
    return pagina, cuadros, False


def dibujar_historia(pantalla, fuente, fuente_chica, pagina, cuadros, velo):
    """Dibuja la página actual de la historia sobre el fondo oscurecido."""
    pantalla.blit(velo, (0, 0))
    pantalla.blit(velo, (0, 0))          # dos veces: más oscuro, para leer bien

    renglones = texto_visible(HISTORIA_INICIO[pagina], cuadros).split("\n")
    alto = fuente.get_height() + 10
    y = ALTO // 2 - (len(renglones) - 1) * alto // 2
    for i in range(len(renglones)):
        menu.escribir(pantalla, fuente, renglones[i], BLANCO, (ANCHO // 2, y + i * alto))

    # puntitos: en qué página estamos
    for i in range(len(HISTORIA_INICIO)):
        x = ANCHO // 2 + (i - (len(HISTORIA_INICIO) - 1) / 2) * 22
        if i == pagina:
            pygame.draw.circle(pantalla, BLANCO, (int(x), ALTO - 90), 5)
        else:
            pygame.draw.circle(pantalla, PLATA, (int(x), ALTO - 90), 3)

    if pagina_completa(pagina, cuadros):
        menu.escribir_aviso(pantalla, fuente_chica, "Pellizcá, Enter o clic para seguir   ·   Esc para saltear",
                                (ANCHO // 2, ALTO - 50))