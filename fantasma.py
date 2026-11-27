# fantasma.py
# La clase Fantasma y las funciones que dibujan los símbolos.

import math
import pygame
from escenario import mezclar, dibujar_brillo, cargar_sprite
from ajustes import (OSO_X, OSO_Y, RADIO_OSO, RADIO_FANTASMA, IMAGEN_FANTASMA, FANTASMA_ALTO,
                     COLOR_FANTASMA, COLOR_OJOS, COLOR_SIMBOLO, CIAN, NOCHE_2)


def crear_sprite_fantasma():
    """Devuelve la imagen del fantasma (img/fantasma.png). Si no está,
    dibuja una vez el cuerpo del fantasma, semitransparente."""
    imagen = cargar_sprite(IMAGEN_FANTASMA, alto=FANTASMA_ALTO)
    if imagen is not None:
        return imagen
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
    """Un espíritu que flota hacia el oso con una fila de sigilos; se espanta cuando se los sacan todos."""
    def __init__(self, x, y, simbolos, velocidad):
        """Crea el fantasma en (x, y) con su lista de sigilos y su velocidad."""
        self.x = x
        self.y = y
        self.simbolos = simbolos  # lista: se borran de a uno, en orden. Vacía = espantado
        self.velocidad = velocidad
        self.herido = 0           # cuadros que titila después de perder un sigilo
        self.fase = x * 0.01     # para que no floten todos sincronizados

    def mover(self):
        """Avanza un paso en línea recta hacia el oso."""
        dx = OSO_X - self.x
        dy = OSO_Y - self.y
        distancia = math.hypot(dx, dy)
        if distancia > 0:
            self.x += dx / distancia * self.velocidad
            self.y += dy / distancia * self.velocidad
        self.fase += 0.08
        if self.herido > 0:
            self.herido -= 1

    def recibir_hechizo(self, simbolo):
        """Si el sigilo coincide con el primero que le queda, se lo saca.
        Devuelve True si acertó."""
        if len(self.simbolos) > 0 and self.simbolos[0] == simbolo:
            self.simbolos.pop(0)
            self.herido = 10
            return True
        return False

    def choca_con_oso(self):
        """Devuelve True si el fantasma llegó al oso."""
        distancia = math.hypot(self.x - OSO_X, self.y - OSO_Y)
        return distancia < RADIO_OSO + RADIO_FANTASMA

    def dibujar(self, pantalla, sprite, brillos):
        """Dibuja el fantasma flotando y, arriba, sus sigilos: el que toca dibujar brilla."""
        if self.herido > 0 and self.herido % 4 < 2:
            return                # titila cuando pierde un sigilo
        x = int(self.x)
        y = int(self.y + math.sin(self.fase) * 4)    # flota subiendo y bajando
        # (x, y) es el centro del fantasma: la imagen se centra ahí
        ancho = sprite.get_width()
        alto = sprite.get_height()
        pantalla.blit(sprite, (x - ancho // 2, y - alto // 2))
        # los sigilos que le quedan, en fila arriba de la cabeza.
        # El primero (el que hay que dibujar ahora) brilla; los otros se ven apagados.
        sy = y - alto // 2 - 22
        separacion = 40
        inicio = x - (len(self.simbolos) - 1) * separacion // 2
        for i in range(len(self.simbolos)):
            sx = inicio + i * separacion
            if i == 0:
                dibujar_brillo(pantalla, brillos, (sx, sy), 0.7)
                dibujar_simbolo(pantalla, self.simbolos[i], sx, sy, 13)
            else:
                dibujar_simbolo(pantalla, self.simbolos[i], sx, sy, 11, apagado=True)


def linea_brillante(pantalla, puntos, apagado=False):
    """Una línea con halo: una gruesa y oscura abajo, una fina y clara arriba.
    apagado=True la dibuja sin brillo (para los sigilos que todavía no tocan)."""
    if apagado:
        pygame.draw.lines(pantalla, mezclar(NOCHE_2, CIAN, 0.45), False, puntos, 3)
        return
    pygame.draw.lines(pantalla, mezclar(NOCHE_2, CIAN, 0.35), False, puntos, 9)
    pygame.draw.lines(pantalla, COLOR_SIMBOLO, False, puntos, 3)


def dibujar_simbolo(pantalla, simbolo, cx, cy, tam, apagado=False):
    """Dibuja el símbolo con líneas, centrado en (cx, cy)."""
    if simbolo == "—":
        puntos = [(cx - tam, cy), (cx + tam, cy)]
    elif simbolo == "|":
        puntos = [(cx, cy - tam), (cx, cy + tam)]
    elif simbolo == "V":
        puntos = [(cx - tam, cy - tam), (cx, cy + tam), (cx + tam, cy - tam)]
    else:   # "Λ"
        puntos = [(cx - tam, cy + tam), (cx, cy - tam), (cx + tam, cy + tam)]
    linea_brillante(pantalla, puntos, apagado)