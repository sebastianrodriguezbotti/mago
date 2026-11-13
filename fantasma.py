# fantasma.py
# La clase Fantasma y las funciones que dibujan los símbolos.

import math
import pygame
from escenario import mezclar, dibujar_brillo
from ajustes import (GATO_X, GATO_Y, RADIO_GATO, RADIO_FANTASMA,
                     COLOR_FANTASMA, COLOR_OJOS, COLOR_SIMBOLO, CIAN, NOCHE_2)


def crear_sprite_fantasma():
    """Dibuja una vez el cuerpo del fantasma, semitransparente, y lo devuelve."""
    r = RADIO_FANTASMA
    sup = pygame.Surface((r * 2, r * 3), pygame.SRCALPHA)
    cuerpo = (*COLOR_FANTASMA, 120)
    pygame.draw.circle(sup, cuerpo, (r, r), r)
    pygame.draw.rect(sup, cuerpo, (0, r, r * 2, r))
    # el borde de abajo, deshilachado
    ancho_fleco = r * 2 / 4
    for i in range(4):
        x0 = i * ancho_fleco
        pygame.draw.polygon(sup, cuerpo, [(x0, r * 2), (x0 + ancho_fleco, r * 2),
                                          (x0 + ancho_fleco / 2, r * 2.7)])
    # ojos huecos
    pygame.draw.ellipse(sup, (*COLOR_OJOS, 230), (r - 13, r - 8, 9, 14))
    pygame.draw.ellipse(sup, (*COLOR_OJOS, 230), (r + 4, r - 8, 9, 14))
    return sup


class Fantasma:
    def __init__(self, x, y, simbolo, velocidad):
        self.x = x
        self.y = y
        self.simbolo = simbolo
        self.velocidad = velocidad
        self.fase = x * 0.01     # para que no floten todos sincronizados

    def mover(self):
        """Avanza un paso en línea recta hacia el gato."""
        dx = GATO_X - self.x
        dy = GATO_Y - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.x += dx / distancia * self.velocidad
            self.y += dy / distancia * self.velocidad
        self.fase += 0.08

    def choca_con_gato(self):
        """Devuelve True si el fantasma llegó al gato."""
        distancia = math.hypot(self.x - GATO_X, self.y - GATO_Y)
        return distancia < RADIO_GATO + RADIO_FANTASMA

    def dibujar(self, pantalla, sprite, brillos):
        x = int(self.x)
        y = int(self.y + math.sin(self.fase) * 4)    # flota subiendo y bajando
        pantalla.blit(sprite, (x - RADIO_FANTASMA, y - RADIO_FANTASMA))
        # el sigilo que hay que dibujar para espantarlo
        sy = y - RADIO_FANTASMA - 24
        dibujar_brillo(pantalla, brillos, (x, sy), 0.7)
        dibujar_simbolo(pantalla, self.simbolo, x, sy, 13)


def linea_brillante(pantalla, puntos):
    """Una línea con halo: una gruesa y oscura abajo, una fina y clara arriba."""
    pygame.draw.lines(pantalla, mezclar(NOCHE_2, CIAN, 0.35), False, puntos, 9)
    pygame.draw.lines(pantalla, COLOR_SIMBOLO, False, puntos, 3)


def dibujar_simbolo(pantalla, simbolo, cx, cy, tam):
    """Dibuja el símbolo con líneas, centrado en (cx, cy)."""
    if simbolo == "—":
        linea_brillante(pantalla, [(cx - tam, cy), (cx + tam, cy)])
    elif simbolo == "|":
        linea_brillante(pantalla, [(cx, cy - tam), (cx, cy + tam)])
    elif simbolo == "V":
        linea_brillante(pantalla, [(cx - tam, cy - tam), (cx, cy + tam), (cx + tam, cy - tam)])
    elif simbolo == "Λ":
        linea_brillante(pantalla, [(cx - tam, cy + tam), (cx, cy - tam), (cx + tam, cy + tam)])