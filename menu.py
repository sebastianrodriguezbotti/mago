# menu.py
# Las pantallas de menú e instrucciones, y el manejo del volumen.

import pygame
from escenario import mezclar
from fantasma import dibujar_simbolo
from ajustes import (ANCHO, ALTO, PASO_VOLUMEN, MENU_Y, MENU_SEPARACION,
                     NOCHE_1, CIAN, PLATA, BLANCO_AZULADO)

OPCIONES = ["Jugar", "Instrucciones", "Volumen", "Salir"]


# ---------- Texto ----------

def escribir(pantalla, fuente, texto, color, centro):
    """Escribe un texto centrado en el punto que se le pasa."""
    sup = fuente.render(texto, True, color)
    rect = sup.get_rect(center=centro)
    pantalla.blit(sup, rect)


def escribir_brillante(pantalla, fuente, texto, centro):
    """Texto cian con un halo suave alrededor."""
    # el halo: el mismo texto en cian oscuro, sobre negro, sumado (BLEND_ADD) varias veces corrido
    halo = fuente.render(texto, True, mezclar(NOCHE_1, CIAN, 0.18), (0, 0, 0))
    rect = halo.get_rect(center=centro)
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        pantalla.blit(halo, rect.move(dx, dy), special_flags=pygame.BLEND_ADD)
    escribir(pantalla, fuente, texto, CIAN, centro)


def escribir_tallado(pantalla, fuente, texto, centro):
    """Texto como tallado en piedra: una sombra oscura corrida y el texto claro arriba."""
    escribir(pantalla, fuente, texto, NOCHE_1, (centro[0] + 3, centro[1] + 3))
    escribir(pantalla, fuente, texto, BLANCO_AZULADO, centro)


def separador(pantalla, centro_y, ancho):
    """Una línea fina de plata con una runa (rombo) en el medio."""
    color = mezclar(NOCHE_1, PLATA, 0.55)
    cx = ANCHO // 2
    pygame.draw.line(pantalla, color, (cx - ancho // 2, centro_y), (cx - 12, centro_y), 1)
    pygame.draw.line(pantalla, color, (cx + 12, centro_y), (cx + ancho // 2, centro_y), 1)
    pygame.draw.polygon(pantalla, color, [(cx, centro_y - 6), (cx + 6, centro_y),
                                          (cx, centro_y + 6), (cx - 6, centro_y)], 1)
    pygame.draw.circle(pantalla, color, (cx - ancho // 2, centro_y), 2)
    pygame.draw.circle(pantalla, color, (cx + ancho // 2, centro_y), 2)


# ---------- Volumen ----------

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


# ---------- Opciones del menú ----------

def texto_opcion(i, volumen):
    """Devuelve el texto que se muestra para la opción i."""
    if OPCIONES[i] == "Volumen":
        return f"‹  Volumen  {int(volumen * 100)}%  ›"
    return OPCIONES[i]


def rect_opcion(fuente, i, volumen):
    """Devuelve el rectángulo que ocupa la opción i en la pantalla."""
    ancho, alto = fuente.size(texto_opcion(i, volumen))
    rect = pygame.Rect(0, 0, ancho + 40, alto + 10)
    rect.center = (ANCHO // 2, MENU_Y + i * MENU_SEPARACION)
    return rect


def opcion_bajo_mouse(fuente, pos, volumen):
    """Devuelve el número de la opción que está bajo el mouse, o None."""
    for i in range(len(OPCIONES)):
        if rect_opcion(fuente, i, volumen).collidepoint(pos):
            return i
    return None


# ---------- Pantallas ----------

def dibujar_menu(pantalla, fuente_titulo, fuente, fuente_chica, seleccion, volumen):
    escribir_tallado(pantalla, fuente_titulo, "El Gato Mago", (ANCHO // 2, 85))
    escribir(pantalla, fuente_chica, "En el bosque dormido, los espíritus despiertan",
             PLATA, (ANCHO // 2, 140))
    separador(pantalla, 168, 360)

    for i in range(len(OPCIONES)):
        centro = (ANCHO // 2, MENU_Y + i * MENU_SEPARACION)
        if i == seleccion:
            escribir_brillante(pantalla, fuente, texto_opcion(i, volumen), centro)
        else:
            escribir(pantalla, fuente, texto_opcion(i, volumen), BLANCO_AZULADO, centro)

    escribir(pantalla, fuente_chica, "Mouse o flechas para elegir  ·  Esc para salir",
             mezclar(NOCHE_1, PLATA, 0.7), (ANCHO // 2, ALTO - 18))


def dibujar_instrucciones(pantalla, fuente_titulo, fuente, fuente_chica):
    # un panel oscuro con marco fino de plata
    panel = pygame.Rect(0, 0, 680, 520)
    panel.center = (ANCHO // 2, ALTO // 2)
    velo = pygame.Surface(panel.size, pygame.SRCALPHA)
    velo.fill((*NOCHE_1, 215))
    pantalla.blit(velo, panel.topleft)
    pygame.draw.rect(pantalla, PLATA, panel, 1)
    pygame.draw.rect(pantalla, mezclar(NOCHE_1, PLATA, 0.4), panel.inflate(-10, -10), 1)

    escribir_tallado(pantalla, fuente_titulo, "Cómo se juega", (ANCHO // 2, panel.top + 50))
    separador(pantalla, panel.top + 92, 300)

    lineas = [
        "Los espíritus del bosque vienen a buscar al gato.",
        "Cada uno lleva un sigilo sobre la cabeza.",
        "Juntá el índice y el pulgar y dibujá ese sigilo en el aire.",
        "Separá los dedos para lanzar el hechizo:",
        "se desvanecen todos los espíritus con ese sigilo.",
        "Si uno toca al gato, perdés una vida. Tenés tres.",
        "Superá los tres niveles y el bosque vuelve a dormir.",
    ]
    for i in range(len(lineas)):
        escribir(pantalla, fuente_chica, lineas[i], BLANCO_AZULADO, (ANCHO // 2, panel.top + 125 + i * 32))

    # los cuatro sigilos que existen
    simbolos = ["—", "|", "V", "Λ"]
    for i in range(len(simbolos)):
        x = ANCHO // 2 - 165 + i * 110
        dibujar_simbolo(pantalla, simbolos[i], x, panel.bottom - 95, 18)

    escribir(pantalla, fuente_chica, "Esc o Enter para volver", PLATA, (ANCHO // 2, panel.bottom - 35))