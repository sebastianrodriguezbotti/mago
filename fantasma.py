# fantasma.py
# La clase Fantasma y las funciones que dibujan los símbolos.

import math
import pygame
from ajustes import (GATO_X, GATO_Y, RADIO_GATO, RADIO_FANTASMA,
                     COLOR_FANTASMA, COLOR_OJOS, COLOR_SIMBOLO)


class Fantasma:
    def __init__(self, x, y, simbolo, velocidad):
        self.x = x
        self.y = y
        self.simbolo = simbolo
        self.velocidad = velocidad

    def mover(self):
        """Avanza un paso en línea recta hacia el gato."""
        dx = GATO_X - self.x
        dy = GATO_Y - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.x += dx / distancia * self.velocidad
            self.y += dy / distancia * self.velocidad

    def choca_con_gato(self):
        """Devuelve True si el fantasma llegó al gato."""
        distancia = math.hypot(self.x - GATO_X, self.y - GATO_Y)
        return distancia < RADIO_GATO + RADIO_FANTASMA

    def dibujar(self, pantalla):
        x = int(self.x)
        y = int(self.y)
        # cuerpo: un círculo arriba y un rectángulo abajo
        pygame.draw.circle(pantalla, COLOR_FANTASMA, (x, y), RADIO_FANTASMA)
        pygame.draw.rect(pantalla, COLOR_FANTASMA,
                         (x - RADIO_FANTASMA, y, RADIO_FANTASMA * 2, RADIO_FANTASMA))
        # ojos
        pygame.draw.circle(pantalla, COLOR_OJOS, (x - 9, y - 4), 5)
        pygame.draw.circle(pantalla, COLOR_OJOS, (x + 9, y - 4), 5)
        # el símbolo que hay que dibujar para eliminarlo
        dibujar_simbolo(pantalla, self.simbolo, x, y - RADIO_FANTASMA - 20, 12)


def dibujar_simbolo(pantalla, simbolo, cx, cy, tam):
    """Dibuja el símbolo con líneas, centrado en (cx, cy)."""
    if simbolo == "—":
        pygame.draw.line(pantalla, COLOR_SIMBOLO, (cx - tam, cy), (cx + tam, cy), 4)
    elif simbolo == "|":
        pygame.draw.line(pantalla, COLOR_SIMBOLO, (cx, cy - tam), (cx, cy + tam), 4)
    elif simbolo == "V":
        puntos = [(cx - tam, cy - tam), (cx, cy + tam), (cx + tam, cy - tam)]
        pygame.draw.lines(pantalla, COLOR_SIMBOLO, False, puntos, 4)
    elif simbolo == "Λ":
        puntos = [(cx - tam, cy + tam), (cx, cy - tam), (cx + tam, cy + tam)]
        pygame.draw.lines(pantalla, COLOR_SIMBOLO, False, puntos, 4)