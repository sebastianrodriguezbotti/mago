# espiritu_piso.py
# El Espíritu del Piso: un fantasma gigante que sube del suelo y golpea donde está el gato.
# Primero marca el lugar en el suelo, y un momento después sale una garra ahí.
# El jugador lo esquiva moviendo la cabeza (el gato sigue a la cabeza).

import math
import pygame
from escenario import mezclar, dibujar_brillo
from ajustes import *


def crear_sprite_gigante():
    """Dibuja una vez el cuerpo del gigante, semitransparente, y lo devuelve."""
    r = ESPIRITU_RADIO
    sup = pygame.Surface((r * 2, r * 3), pygame.SRCALPHA)
    cuerpo = (*COLOR_FANTASMA, 105)
    pygame.draw.circle(sup, cuerpo, (r, r), r)
    pygame.draw.rect(sup, cuerpo, (0, r, r * 2, r * 2))
    # ojos huecos, grandes y rasgados
    pygame.draw.ellipse(sup, (*NOCHE_1, 235), (r - 62, r - 30, 42, 58))
    pygame.draw.ellipse(sup, (*NOCHE_1, 235), (r + 20, r - 30, 42, 58))
    # boca
    pygame.draw.ellipse(sup, (*NOCHE_1, 200), (r - 30, r + 45, 60, 34))
    return sup


def crear_garra():
    """Dibuja una vez la garra que sale del piso: una columna que se desvanece hacia arriba."""
    ancho = ESPIRITU_ANCHO_GOLPE
    alto = ESPIRITU_ALTO_GOLPE
    sup = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y in range(alto):
        alfa = int(190 * y / alto)            # transparente arriba, espesa abajo
        pygame.draw.line(sup, (*COLOR_FANTASMA, alfa), (8, y), (ancho - 8, y))
    # tres dedos en punta, arriba
    for i in range(3):
        x0 = 8 + i * (ancho - 16) // 3
        x1 = x0 + (ancho - 16) // 3
        pygame.draw.polygon(sup, (*COLOR_FANTASMA, 120), [(x0, 40), (x1, 40), ((x0 + x1) // 2, 0)])
    # bordes cian: es magia
    pygame.draw.line(sup, CIAN, (8, 30), (8, alto), 2)
    pygame.draw.line(sup, CIAN, (ancho - 8, 30), (ancho - 8, alto), 2)
    return sup


class EspirituDelPiso:
    def __init__(self, cantidad_ataques):
        self.fase = "subiendo"       # "subiendo", "atacando", "bajando" o "terminado"
        self.altura = 0.0            # 0 = escondido bajo el piso, 1 = afuera del todo
        self.ataques_restantes = cantidad_ataques
        self.espera = ESPIRITU_PAUSA # cuadros hasta marcar el próximo ataque
        self.ataque_x = None         # dónde va a golpear (None si no hay ataque en curso)
        self.aviso = 0               # cuadros que le quedan a la marca antes del golpe
        self.golpe = 0               # cuadros que le quedan a la garra afuera
        self.tiempo = 0
        self.sprite = crear_sprite_gigante()
        self.garra = crear_garra()

    def actualizar(self, gato_x):
        """Avanza un cuadro. Devuelve "dano" si un golpe alcanzó al gato,
        "golpe" si golpeó y el gato lo esquivó, o None."""
        self.tiempo += 1
        resultado = None

        if self.fase == "subiendo":
            self.altura += 1 / ESPIRITU_SUBIR
            if self.altura >= 1:
                self.altura = 1
                self.fase = "atacando"

        elif self.fase == "atacando":
            if self.golpe > 0:
                # la garra está afuera: espera a que se esconda
                self.golpe -= 1
                if self.golpe == 0:
                    self.ataque_x = None
                    self.ataques_restantes -= 1
                    self.espera = ESPIRITU_PAUSA
                    if self.ataques_restantes == 0:
                        self.fase = "bajando"
            elif self.ataque_x is not None:
                # hay una marca en el suelo: cuenta hacia atrás y golpea
                self.aviso -= 1
                if self.aviso == 0:
                    self.golpe = ESPIRITU_GOLPE
                    if self.alcanza(gato_x):
                        resultado = "dano"
                    else:
                        resultado = "golpe"
            else:
                # no hay ataque: espera y después apunta a donde está el gato AHORA
                self.espera -= 1
                if self.espera <= 0:
                    self.ataque_x = gato_x
                    self.aviso = ESPIRITU_AVISO

        elif self.fase == "bajando":
            self.altura -= 1 / ESPIRITU_SUBIR
            if self.altura <= 0:
                self.altura = 0
                self.fase = "terminado"

        return resultado

    def alcanza(self, gato_x):
        """Devuelve True si el gato está dentro de la zona del golpe."""
        return abs(gato_x - self.ataque_x) < ESPIRITU_ANCHO_GOLPE / 2 + RADIO_GATO * 0.6

    def dibujar_gigante(self, pantalla, brillos):
        """El gigante, asomando detrás del piso. Va antes de dibujar el piso."""
        if self.altura <= 0:
            return
        x = ANCHO // 2 + math.sin(self.tiempo * 0.03) * 40        # se balancea despacio
        y = ALTO + ESPIRITU_RADIO - self.altura * ESPIRITU_RADIO * 2.4
        pantalla.blit(self.sprite, (int(x) - ESPIRITU_RADIO, int(y) - ESPIRITU_RADIO))
        # los ojos le brillan en cian, más fuerte cuando está por golpear
        fuerza = 0.5
        if self.ataque_x is not None and self.golpe == 0:
            fuerza = 1
        for dx in (-41, 41):
            dibujar_brillo(pantalla, brillos, (x + dx, y), fuerza)
            pygame.draw.circle(pantalla, CIAN_CLARO, (int(x + dx), int(y)), 6)

    def dibujar_ataque(self, pantalla, brillos):
        """La marca en el suelo y la garra. Va después del gato: la garra lo tapa."""
        if self.ataque_x is None:
            return
        x = int(self.ataque_x)
        if self.golpe == 0:
            # la marca: titila cada vez más rápido y más fuerte a medida que se acerca el golpe
            falta = self.aviso / ESPIRITU_AVISO              # 1 al principio, 0 al golpear
            titila = 0.5 + 0.5 * math.sin(self.tiempo * (0.3 + (1 - falta) * 0.9))
            k = (1 - falta) * 0.6 + 0.4 * titila
            rect = pygame.Rect(0, 0, ESPIRITU_ANCHO_GOLPE, 24)
            rect.center = (x, SUELO_Y)
            pygame.draw.ellipse(pantalla, mezclar(NOCHE_2, CIAN, k * 0.5), rect)
            pygame.draw.ellipse(pantalla, mezclar(NOCHE_2, CIAN_CLARO, k), rect, 2)
            dibujar_brillo(pantalla, brillos, (x, SUELO_Y), k)
        else:
            # la garra: sale rápido en los primeros cuadros
            salida = min(1, (ESPIRITU_GOLPE - self.golpe + 1) / 4)
            alto = int(ESPIRITU_ALTO_GOLPE * salida)
            recorte = self.garra.subsurface((0, 0, ESPIRITU_ANCHO_GOLPE, alto))
            pantalla.blit(recorte, (x - ESPIRITU_ANCHO_GOLPE // 2, SUELO_Y - alto))
            dibujar_brillo(pantalla, brillos, (x, SUELO_Y), 1)