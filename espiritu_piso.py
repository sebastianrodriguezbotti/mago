# espiritu_piso.py
# El Espíritu del Piso: un fantasma gigante que sube del suelo y golpea donde está el oso.
# Primero marca el lugar en el suelo, y un momento después sale una garra ahí.
# El jugador lo esquiva moviendo la cabeza (el oso sigue a la cabeza).
#
# En el nivel 5 es el jefe (jefe=True): tiene vida y está todo el nivel.
# Alterna rondas de ataques con momentos en que queda "vulnerable": muestra un sigilo
# y, si el jugador lo dibuja con la mano, le saca vida.

import math
import random
import pygame
from escenario import mezclar, dibujar_brillo, cargar_sprite
from fantasma import dibujar_simbolo
from ajustes import *


def dibujar_sprite_gigante():
    """Dibuja una vez el gigante con formas, semitransparente (si no hay imagen)."""
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


# Las imágenes se cargan una sola vez, con cargar_imagenes(), antes del bucle principal.
imagenes = {"gigante": None, "garra": None, "con_imagen": False}


def cargar_imagenes():
    """Carga (o dibuja) una sola vez el gigante y la garra. Se llama desde main antes del bucle."""
    imagen = cargar_sprite(IMAGEN_JEFE, ancho=JEFE_ANCHO)    # img/jefe.png
    imagenes["con_imagen"] = imagen is not None
    if imagen is not None:
        imagenes["gigante"] = imagen
    else:
        imagenes["gigante"] = dibujar_sprite_gigante()
    imagenes["garra"] = crear_garra()


class EspirituDelPiso:
    def __init__(self, cantidad_ataques, jefe=False):
        # fases: "subiendo", "atacando", "vulnerable" (solo el jefe), "bajando", "terminado"
        self.fase = "subiendo"
        self.jefe = jefe
        self.vida = JEFE_VIDA
        self.altura = 0.0            # 0 = escondido bajo el piso, 1 = afuera del todo
        self.ataques_por_ronda = cantidad_ataques
        self.ataques_restantes = cantidad_ataques
        self.espera = ESPIRITU_PAUSA # cuadros hasta marcar el próximo ataque
        self.ataque_x = None         # dónde va a golpear (None si no hay ataque en curso)
        self.aviso = 0               # cuadros que le quedan a la marca antes del golpe
        self.golpe = 0               # cuadros que le quedan a la garra afuera
        self.simbolo = None          # el sigilo que muestra cuando está vulnerable
        self.vulnerable = 0          # cuadros que le quedan descubierto
        self.herido = 0              # cuadros que titila después de recibir un hechizo
        self.tiempo = 0
        self.sprite = imagenes["gigante"]
        self.garra = imagenes["garra"]
        self.con_imagen = imagenes["con_imagen"]

    def posicion(self):
        """Devuelve (x, y): dónde está el centro de la cabeza ahora."""
        x = ANCHO // 2 + math.sin(self.tiempo * 0.03) * 40        # se balancea despacio
        escondido = ALTO + ESPIRITU_RADIO                          # abajo del borde de la pantalla
        y = escondido + (ESPIRITU_Y - escondido) * self.altura
        return (x, y)

    def actualizar(self, oso_x):
        """Avanza un cuadro. Devuelve "dano" si un golpe alcanzó al oso,
        "golpe" si golpeó y el oso lo esquivó, o None."""
        self.tiempo += 1
        if self.herido > 0:
            self.herido -= 1
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
                    self.terminar_ataque()
            elif self.ataque_x is not None:
                # hay una marca en el suelo: cuenta hacia atrás y golpea
                self.aviso -= 1
                if self.aviso == 0:
                    self.golpe = ESPIRITU_GOLPE
                    if self.alcanza(oso_x):
                        resultado = "dano"
                    else:
                        resultado = "golpe"
            else:
                # no hay ataque: espera y después apunta a donde está el oso AHORA
                self.espera -= 1
                if self.espera <= 0:
                    self.ataque_x = oso_x
                    self.aviso = ESPIRITU_AVISO

        elif self.fase == "vulnerable":
            self.vulnerable -= 1
            if self.vulnerable <= 0:
                # se le acabó el tiempo descubierto: otra ronda de ataques
                self.fase = "atacando"
                self.simbolo = None
                self.ataques_restantes = self.ataques_por_ronda
                self.espera = ESPIRITU_PAUSA

        elif self.fase == "bajando":
            self.altura -= 1 / ESPIRITU_SUBIR
            if self.altura <= 0:
                self.altura = 0
                self.fase = "terminado"

        return resultado

    def terminar_ataque(self):
        """Termina un ataque y decide qué sigue: otro ataque, descubrirse o irse."""
        self.ataque_x = None
        self.ataques_restantes -= 1
        self.espera = ESPIRITU_PAUSA
        if self.ataques_restantes == 0:
            if self.jefe:
                self.fase = "vulnerable"
                self.vulnerable = JEFE_VULNERABLE
                self.simbolo = random.choice(SIMBOLOS)
            else:
                self.fase = "bajando"

    def recibir_hechizo(self, simbolo):
        """El jugador dibujó un sigilo. Devuelve True si le hizo daño."""
        if self.fase != "vulnerable" or simbolo != self.simbolo:
            return False
        self.vida -= JEFE_DANO
        self.herido = 12
        if self.vida <= 0:
            self.vida = 0
            self.fase = "bajando"
            self.simbolo = None
        else:
            # otro sigilo distinto al anterior
            otros = [s for s in SIMBOLOS if s != simbolo]
            self.simbolo = random.choice(otros)
        return True

    def derrotado(self):
        """Devuelve True si es el jefe y se quedó sin vida."""
        return self.jefe and self.vida <= 0

    def alcanza(self, oso_x):
        """Devuelve True si el oso está dentro de la zona del golpe."""
        return abs(oso_x - self.ataque_x) < ESPIRITU_ANCHO_GOLPE / 2 + RADIO_OSO * 0.6

    def dibujar_gigante(self, pantalla, brillos):
        """El gigante, asomando detrás del piso. Va antes de dibujar el piso."""
        if self.altura <= 0:
            return
        if self.herido > 0 and self.herido % 4 < 2:
            return                   # titila cuando recibe un hechizo
        x, y = self.posicion()
        ancho = self.sprite.get_width()
        pantalla.blit(self.sprite, (int(x) - ancho // 2, int(y) - ESPIRITU_RADIO))
        if self.con_imagen:
            return                   # con imagen, los ojos ya vienen en el dibujo
        # los ojos le brillan en cian, más fuerte cuando está por golpear
        fuerza = 0.5
        if self.ataque_x is not None and self.golpe == 0:
            fuerza = 1
        if self.fase == "vulnerable":
            fuerza = 0.2             # descubierto: los ojos se apagan
        for dx in (-41, 41):
            dibujar_brillo(pantalla, brillos, (x + dx, y), fuerza)
            pygame.draw.circle(pantalla, mezclar(NOCHE_2, CIAN_CLARO, 0.4 + 0.6 * fuerza),
                               (int(x + dx), int(y)), 6)

    def dibujar_sigilo(self, pantalla, brillos):
        """Cuando está vulnerable, el sigilo que hay que dibujar, arriba de la cabeza.
        Va encima del piso, para que se vea siempre."""
        if self.fase != "vulnerable" or self.simbolo is None:
            return
        x, y = self.posicion()
        sy = int(y - ESPIRITU_RADIO - 45)
        dibujar_brillo(pantalla, brillos, (x, sy), 1)
        dibujar_simbolo(pantalla, self.simbolo, int(x), sy, 26)
        # una barrita debajo del sigilo: el tiempo que le queda descubierto
        ancho = int(120 * self.vulnerable / JEFE_VULNERABLE)
        pygame.draw.line(pantalla, CIAN, (int(x) - ancho // 2, sy + 42), (int(x) + ancho // 2, sy + 42), 3)

    def dibujar_ataque(self, pantalla, brillos):
        """La marca en el suelo y la garra. Va después del oso: la garra lo tapa."""
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