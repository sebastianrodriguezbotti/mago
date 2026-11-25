# escenario.py
# El "Bosque Espectral": todo lo que se ve y no es parte de las reglas del juego.
# Fondo de árboles, niebla, fuegos fatuos, círculo de piedras, el oso y los efectos de luz.
#
# Idea clave de la luz: una "mancha de luz" es un círculo que va de cian en el centro
# a negro en el borde. Se pega con BLEND_ADD, que SUMA los colores: el negro no
# cambia nada y el cian aclara lo que hay abajo. Así parece que la luz ilumina la niebla.

import math
import os
import random
import pygame
from ajustes import *


# ---------- Ayudas de color, letra y luz ----------

def mezclar(color1, color2, k):
    """Devuelve un color entre color1 (k=0) y color2 (k=1)."""
    r = int(color1[0] + (color2[0] - color1[0]) * k)
    g = int(color1[1] + (color2[1] - color1[1]) * k)
    b = int(color1[2] + (color2[2] - color1[2]) * k)
    return (r, g, b)


def cargar_fuente(archivo, tamano):
    """Carga una fuente de la carpeta fuentes/. Si no está, usa una parecida de Windows."""
    ruta = os.path.join("fuentes", archivo)
    if os.path.exists(ruta):
        return pygame.font.Font(ruta, tamano)
    if archivo == FUENTE_TITULO:
        return pygame.font.SysFont(RESPALDO_TITULO, tamano)
    return pygame.font.SysFont(RESPALDO_TEXTO, tamano)


def cargar_imagen_fondo(ruta_sin_extension, capa=False):
    """Carga una imagen de fondo. Devuelve None si no existe.
    Normal: la estira al tamaño de la ventana.
    capa=True: respeta las partes transparentes del PNG y la lleva al ancho de la
    ventana sin deformarla (el alto cambia en la misma proporción)."""
    for extension in (".png", ".jpg", ".jpeg"):
        ruta = ruta_sin_extension + extension
        if os.path.exists(ruta):
            if not capa:
                imagen = pygame.image.load(ruta).convert()
                return pygame.transform.smoothscale(imagen, (ANCHO, ALTO))
            imagen = pygame.image.load(ruta).convert_alpha()
            alto = int(imagen.get_height() * ANCHO / imagen.get_width())
            return pygame.transform.smoothscale(imagen, (ANCHO, alto))
    print("No encontré la imagen", ruta_sin_extension, "- uso el bosque dibujado")
    return None


def cargar_sprite(ruta_sin_extension, alto=None, ancho=None):
    """Carga la imagen de un personaje (PNG con transparencia) y la escala sin deformarla:
    a la altura alto, o al ancho ancho. Devuelve None si no existe."""
    ruta = ruta_sin_extension + ".png"
    if not os.path.exists(ruta):
        print("No encontré", ruta, "- lo dibujo con código")
        return None
    imagen = pygame.image.load(ruta).convert_alpha()
    if alto is not None:
        ancho = int(imagen.get_width() * alto / imagen.get_height())
    else:
        alto = int(imagen.get_height() * ancho / imagen.get_width())
    return pygame.transform.smoothscale(imagen, (ancho, alto))


def crear_brillos(radio, color, niveles):
    """Devuelve una lista de manchas de luz, de la más tenue a la más fuerte."""
    lista = []
    for n in range(1, niveles + 1):
        fuerza = n / niveles
        sup = pygame.Surface((radio * 2, radio * 2))   # empieza toda negra
        paso = max(1, radio // 60)    # las manchas grandes, de a varios píxeles: es más rápido
        for r in range(radio, 0, -paso):
            k = fuerza * (1 - r / radio) ** 2
            pygame.draw.circle(sup, mezclar((0, 0, 0), color, k), (radio, radio), r)
        lista.append(sup)
    return lista


def dibujar_brillo(pantalla, brillos, centro, intensidad):
    """Suma una mancha de luz en centro. intensidad va de 0 a 1."""
    i = int(intensidad * (len(brillos) - 1))
    i = max(0, min(len(brillos) - 1, i))
    sup = brillos[i]
    r = sup.get_width() // 2
    pantalla.blit(sup, (int(centro[0]) - r, int(centro[1]) - r), special_flags=pygame.BLEND_ADD)


def dibujar_trazo(pantalla, puntos):
    """El trazo de la varita: tres líneas una encima de otra hacen el brillo."""
    if len(puntos) < 2:
        return
    pygame.draw.lines(pantalla, mezclar(NOCHE_2, CIAN, 0.35), False, puntos, 14)
    pygame.draw.lines(pantalla, CIAN, False, puntos, 7)
    pygame.draw.lines(pantalla, CIAN_CLARO, False, puntos, 3)


def dibujar_cursor(pantalla, brillos, pos):
    """El cursor es un fuego fatuo chiquito."""
    dibujar_brillo(pantalla, brillos, pos, 1)
    pygame.draw.circle(pantalla, CIAN_CLARO, pos, 4)


# ---------- Árboles ----------

def crear_arbol(x, base_y, altura, grosor, inclinacion):
    """Devuelve la lista de ramas de un árbol seco. Cada rama es (inicio, fin, grosor)."""
    ramas = []
    agregar_rama(ramas, (x, base_y), -90 + inclinacion, altura * 0.36, grosor, 0)
    # raíces: unas pocas ramas cortas que salen hacia los costados
    for i in range(3):
        angulo = random.choice([random.uniform(5, 35), random.uniform(145, 175)])
        largo = random.uniform(20, 45)
        fin = (x + math.cos(math.radians(angulo)) * largo,
               base_y + math.sin(math.radians(angulo)) * largo * 0.4)
        ramas.append(((x, base_y - 4), fin, grosor * 0.45))
    return ramas


def agregar_rama(ramas, inicio, angulo, largo, grosor, nivel):
    """Agrega una rama torcida y, al final, de 2 a 3 ramas más chicas (recursivo)."""
    if nivel > 5 or grosor < 1:
        return
    # la rama se tuerce: va en dos tramos con ángulos un poco distintos
    angulo1 = angulo + random.uniform(-14, 14)
    medio = (inicio[0] + math.cos(math.radians(angulo1)) * largo / 2,
             inicio[1] + math.sin(math.radians(angulo1)) * largo / 2)
    angulo2 = angulo + random.uniform(-14, 14)
    fin = (medio[0] + math.cos(math.radians(angulo2)) * largo / 2,
           medio[1] + math.sin(math.radians(angulo2)) * largo / 2)
    ramas.append((inicio, medio, grosor))
    ramas.append((medio, fin, grosor * 0.85))

    for i in range(random.choice([2, 2, 3])):
        nuevo = angulo2 + random.uniform(-48, 48)
        nuevo = max(-172, min(-8, nuevo))      # que siempre crezcan hacia arriba
        agregar_rama(ramas, fin, nuevo, largo * random.uniform(0.6, 0.8), grosor * 0.62, nivel + 1)


def dibujar_arbol(sup, ramas, color):
    for inicio, fin, grosor in ramas:
        pygame.draw.line(sup, color, inicio, fin, max(1, int(grosor)))
        if grosor > 3:   # tapa la unión entre tramos
            pygame.draw.circle(sup, color, (int(fin[0]), int(fin[1])), int(grosor / 2))


# ---------- Fondo y niebla (se crean una sola vez) ----------

def banda_niebla(alto, alfa_max):
    """Una franja de niebla que se hace más espesa hacia abajo."""
    sup = pygame.Surface((ANCHO, alto), pygame.SRCALPHA)
    for y in range(alto):
        alfa = int(alfa_max * y / alto)
        pygame.draw.line(sup, (*GRIS_AZUL, alfa), (0, y), (ANCHO, y))
    return sup


def crear_mancha_niebla(ancho, alto):
    """Una nube suave: elipses una adentro de otra, más espesas en el centro."""
    mancha = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for i in range(5):
        k = i / 5
        rect = pygame.Rect(0, 0, int(ancho * (1 - k * 0.8)), int(alto * (1 - k * 0.8)))
        rect.center = (ancho // 2, alto // 2)
        pygame.draw.ellipse(mancha, (*GRIS_AZUL, 6 + i * 6), rect)
    return mancha


def crear_niebla():
    """Una tira de niebla del doble del ancho, que empalma en los bordes para poder repetirse."""
    ancho = ANCHO * 2
    alto = 220
    sup = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for i in range(45):
        w = random.randint(180, 380)
        h = random.randint(50, 110)
        x = random.randint(0, ancho)
        y = random.randint(30, alto - h)
        mancha = crear_mancha_niebla(w, h)
        for corrimiento in (-ancho, 0, ancho):   # repetida a los costados: así empalma
            sup.blit(mancha, (x - w // 2 + corrimiento, y))
    return sup


def crear_fondo():
    """Dibuja una vez el bosque quieto: cielo, tres capas de árboles, niebla, suelo y hongos."""
    fondo = pygame.Surface((ANCHO, ALTO))

    # cielo: de negro arriba a azul noche cerca del horizonte
    for y in range(ALTO):
        k = y / ALTO
        if k < 0.65:
            color = mezclar(NOCHE_1, NOCHE_3, k / 0.65)
        else:
            color = mezclar(NOCHE_3, NOCHE_2, (k - 0.65) / 0.35)
        pygame.draw.line(fondo, color, (0, y), (ANCHO, y))

    # capas de árboles, de la más lejana a la más cercana.
    # Las lejanas son más claras: se pierden en la niebla. Eso da profundidad.
    capas = [
        # (color, cantidad, base_y, altura mínima, altura máxima, grosor)
        (mezclar(NOCHE_3, GRIS_AZUL, 0.6), 16, int(ALTO * 0.70), 220, 320, 7),
        (mezclar(NOCHE_2, GRIS_AZUL, 0.25), 10, int(ALTO * 0.80), 300, 420, 11),
    ]
    for color, cantidad, base_y, alto_min, alto_max, grosor in capas:
        for i in range(cantidad):
            x = random.randint(0, ANCHO)
            arbol = crear_arbol(x, base_y, random.randint(alto_min, alto_max), grosor,
                                random.uniform(-8, 8))
            dibujar_arbol(fondo, arbol, color)
        niebla = banda_niebla(140, 110)
        fondo.blit(niebla, (0, base_y - 120))

    # suelo con borde de musgo
    borde = []
    for x in range(0, ANCHO + 40, 40):
        borde.append((x, ALTO - 95 + random.randint(-8, 8)))
    pygame.draw.polygon(fondo, NOCHE_1, borde + [(ANCHO, ALTO), (0, ALTO)])
    pygame.draw.lines(fondo, MUSGO, False, borde, 3)

    # árboles cercanos (lejos del centro, para no tapar el círculo)
    for i in range(4):
        if i % 2 == 0:
            x = random.randint(90, int(ANCHO * 0.28))
        else:
            x = random.randint(int(ANCHO * 0.72), ANCHO - 90)
        arbol = crear_arbol(x, ALTO - 85, random.randint(420, 520), 15, random.uniform(-6, 6))
        dibujar_arbol(fondo, arbol, mezclar(NOCHE_1, NOCHE_2, 0.6))

    # hongos que brillan, chiquitos, en el suelo
    luz_hongo = crear_brillos(10, CIAN, 6)
    for i in range(16):
        x = random.randint(20, ANCHO - 20)
        if abs(x - CIRCULO_X) < CIRCULO_RADIO_X + 20:
            continue    # no en el círculo de piedras
        y = random.randint(ALTO - 90, ALTO - 30)
        for j in range(random.randint(1, 3)):
            hx = x + j * 7
            pygame.draw.line(fondo, mezclar(NOCHE_2, PLATA, 0.4), (hx, y), (hx, y - 6), 2)
            pygame.draw.ellipse(fondo, mezclar(NOCHE_2, CIAN, 0.7), (hx - 4, y - 10, 9, 5))
            dibujar_brillo(fondo, luz_hongo, (hx, y - 8), 0.6)

    return fondo


# ---------- Fuegos fatuos ----------

class FuegoFatuo:
    def __init__(self):
        self.x = random.uniform(40, ANCHO - 40)
        self.y = random.uniform(ALTO * 0.2, ALTO * 0.8)
        self.angulo = random.uniform(0, 360)
        self.fase = random.uniform(0, 6.28)
        self.velocidad = VELOCIDAD_FUEGOS * random.uniform(0.6, 1.3)

    def mover(self):
        # cambia un poquito de dirección en cada cuadro: el camino es suave pero impredecible
        self.angulo += random.uniform(-12, 12)
        # si se aleja mucho, gira de a poco hacia el centro del bosque
        if self.x < 60 or self.x > ANCHO - 60 or self.y < ALTO * 0.15 or self.y > ALTO * 0.85:
            hacia = math.degrees(math.atan2(ALTO * 0.5 - self.y, ANCHO / 2 - self.x))
            diferencia = (hacia - self.angulo + 180) % 360 - 180
            self.angulo += diferencia * 0.15
        self.x += math.cos(math.radians(self.angulo)) * self.velocidad
        self.y += math.sin(math.radians(self.angulo)) * self.velocidad * 0.6 + math.sin(self.fase) * 0.3
        self.fase += 0.06

    def intensidad(self):
        """Devuelve cuánto brilla ahora, entre 0.1 y 1: late despacio."""
        return 0.55 + 0.45 * math.sin(self.fase)

    def dibujar(self, pantalla, brillos):
        dibujar_brillo(pantalla, brillos, (self.x, self.y), self.intensidad())
        pygame.draw.circle(pantalla, CIAN_CLARO, (int(self.x), int(self.y)), 2)


# ---------- Sigilos del círculo de piedras ----------

def dibujar_sigilo(pantalla, tipo, cx, cy, tam, color):
    """Formas geométricas perfectas: marcan dónde está la magia."""
    if tipo == 0:
        pygame.draw.circle(pantalla, color, (cx, cy), tam, 2)
        pygame.draw.line(pantalla, color, (cx, cy - tam - 3), (cx, cy + tam + 3), 2)
    elif tipo == 1:
        puntos = [(cx, cy - tam), (cx + tam, cy + tam), (cx - tam, cy + tam)]
        pygame.draw.polygon(pantalla, color, puntos, 2)
    elif tipo == 2:
        puntos = [(cx, cy - tam), (cx + tam, cy), (cx, cy + tam), (cx - tam, cy)]
        pygame.draw.polygon(pantalla, color, puntos, 2)
        pygame.draw.circle(pantalla, color, (cx, cy), 2)
    else:
        pygame.draw.circle(pantalla, color, (cx, cy), tam, 2)
        pygame.draw.line(pantalla, color, (cx - tam + 3, cy), (cx + tam - 3, cy), 2)
        pygame.draw.circle(pantalla, color, (cx, cy), 3)


def crear_piedras():
    """Devuelve la lista de piedras del círculo, ordenada de atrás hacia adelante."""
    piedras = []
    centro_y = CIRCULO_Y
    for i in range(CANTIDAD_PIEDRAS):
        angulo = math.radians(360 * i / CANTIDAD_PIEDRAS - 90)
        x = CIRCULO_X + math.cos(angulo) * CIRCULO_RADIO_X
        y = centro_y + math.sin(angulo) * CIRCULO_RADIO_Y
        # las de adelante (y más grande) se ven más grandes
        escala = 0.7 + 0.3 * (math.sin(angulo) + 1) / 2
        alto = ALTO_PIEDRA * escala * random.uniform(0.85, 1.15)
        ancho = 22 * escala
        forma = [(-ancho / 2, 0), (-ancho / 2 + random.uniform(0, 3), -alto * 0.8),
                 (random.uniform(-4, 4), -alto), (ancho / 2 - random.uniform(0, 3), -alto * 0.85),
                 (ancho / 2, 0)]
        piedras.append({"x": x, "y": y, "forma": forma, "alto": alto,
                        "sigilo": i % 4, "desfase": i * 0.7, "adelante": y > centro_y})
    piedras.sort(key=lambda p: p["y"])
    return piedras


# ---------- El bosque entero ----------

class Bosque:
    def __init__(self):
        # todo esto se crea una sola vez
        self.fondo = crear_fondo()
        self.niebla = crear_niebla()
        self.niebla_frente = self.niebla.copy()
        self.niebla_frente.set_alpha(140)
        self.brillo_fuego = crear_brillos(28, CIAN, 10)
        self.brillo_chico = crear_brillos(12, CIAN, 10)
        self.brillo_circulo = crear_brillos(240, CIAN, 10)
        self.piedras = crear_piedras()
        self.fuegos = []
        for i in range(CANTIDAD_FUEGOS):
            self.fuegos.append(FuegoFatuo())
        # dos árboles grandes adelante, en los bordes, inclinados hacia adentro: "encierran"
        self.arboles_frente = [
            {"ramas": crear_arbol(30, ALTO + 10, 640, 24, 10), "base_y": ALTO + 10, "altura": 640},
            {"ramas": crear_arbol(ANCHO - 30, ALTO + 10, 640, 24, -10), "base_y": ALTO + 10, "altura": 640},
        ]
        self.imagen_oso = cargar_sprite(IMAGEN_OSO, alto=OSO_ALTO)   # None si no está
        self.tiempo = 0
        self.niebla_x = 0
        self.viento = 0
        self.viento_objetivo = 0
        self.ojos = None     # [x, y, vida] cuando hay ojos mirando

    def respirar(self, desfase):
        """Devuelve un brillo entre 0 y 1 que sube y baja despacio."""
        return 0.5 + 0.5 * math.sin(self.tiempo * VELOCIDAD_RESPIRAR + desfase)

    def actualizar(self):
        self.tiempo += 1
        self.niebla_x += VELOCIDAD_NIEBLA
        for f in self.fuegos:
            f.mover()

        # ráfagas de viento: de vez en cuando las ramas se doblan y vuelven
        if self.viento_objetivo == 0 and random.random() < PROBABILIDAD_RAFAGA:
            self.viento_objetivo = random.choice([-1, 1]) * FUERZA_RAFAGA
        self.viento += (self.viento_objetivo - self.viento) * 0.05
        if self.viento_objetivo != 0 and abs(self.viento_objetivo - self.viento) < 1:
            self.viento_objetivo = 0

        # ojos entre los árboles
        if self.ojos is None and random.random() < PROBABILIDAD_OJOS:
            if random.random() < 0.5:
                x = random.randint(70, int(ANCHO * 0.28))
            else:
                x = random.randint(int(ANCHO * 0.72), ANCHO - 70)
            self.ojos = [x, random.randint(int(ALTO * 0.40), int(ALTO * 0.62)), 110]
        if self.ojos is not None:
            self.ojos[2] -= 1
            if self.ojos[2] <= 0:
                self.ojos = None

    def dibujar_fondo(self, pantalla):
        pantalla.blit(self.fondo, (0, 0))
        # la luz del círculo de piedras, que ilumina la niebla del fondo
        dibujar_brillo(pantalla, self.brillo_circulo, (CIRCULO_X, CIRCULO_Y - 15), 0.25 + 0.15 * self.respirar(0))
        self.dibujar_ojos(pantalla)
        self.dibujar_niebla(pantalla, self.niebla, ALTO - 260, self.niebla_x)
        for f in self.fuegos:
            f.dibujar(pantalla, self.brillo_fuego)

    def dibujar_fuegos(self, pantalla):
        """Solo los fuegos fatuos: para cuando el fondo es una imagen."""
        for f in self.fuegos:
            f.dibujar(pantalla, self.brillo_fuego)

    def dibujar_ojos(self, pantalla):
        if self.ojos is None:
            return
        x, y, vida = self.ojos
        if 50 < vida < 56:
            return              # parpadeo
        k = min(1, vida / 20, (110 - vida) / 20)   # aparecen y se van de a poco
        for dx in (-7, 7):
            dibujar_brillo(pantalla, self.brillo_chico, (x + dx, y), k * 0.6)
            pygame.draw.circle(pantalla, mezclar(NOCHE_1, CIAN_CLARO, k), (x + dx, y), 2)

    def dibujar_niebla(self, pantalla, niebla, y, corrimiento):
        ancho = niebla.get_width()
        x = int(corrimiento) % ancho
        pantalla.blit(niebla, (x - ancho, y))
        pantalla.blit(niebla, (x, y))

    def dibujar_piedras(self, pantalla, adelante):
        """Dibuja las piedras de atrás (adelante=False) o las de adelante (True)."""
        centro_y = CIRCULO_Y
        if not adelante:
            # el anillo tallado en el suelo
            k = self.respirar(0)
            rect = pygame.Rect(0, 0, CIRCULO_RADIO_X * 2 + 30, CIRCULO_RADIO_Y * 2 + 10)
            rect.center = (CIRCULO_X, centro_y)
            pygame.draw.ellipse(pantalla, mezclar(NOCHE_2, CIAN, 0.25 + 0.35 * k), rect, 2)
            rect.inflate_ip(-50, -14)
            pygame.draw.ellipse(pantalla, mezclar(NOCHE_2, CIAN, 0.15 + 0.2 * k), rect, 1)

        for p in self.piedras:
            if p["adelante"] != adelante:
                continue
            puntos = [(p["x"] + dx, p["y"] + dy) for dx, dy in p["forma"]]
            pygame.draw.polygon(pantalla, GRIS_AZUL, puntos)
            # sombra en la mitad izquierda, la luz viene del centro del círculo
            sombra = [puntos[0], puntos[1], puntos[2], (p["x"], p["y"])]
            pygame.draw.polygon(pantalla, mezclar(NOCHE_3, GRIS_AZUL, 0.4), sombra)
            pygame.draw.polygon(pantalla, NOCHE_1, puntos, 1)
            # musgo arriba
            pygame.draw.circle(pantalla, MUSGO, (int(puntos[2][0]), int(puntos[2][1]) + 3), 4)
            # el sigilo tallado, que respira
            k = self.respirar(p["desfase"])
            cx = int(p["x"])
            cy = int(p["y"] - p["alto"] * 0.5)
            dibujar_brillo(pantalla, self.brillo_chico, (cx, cy), 0.3 + 0.7 * k)
            dibujar_sigilo(pantalla, p["sigilo"], cx, cy, 6, mezclar(NOCHE_3, CIAN_CLARO, 0.3 + 0.7 * k))

    def dibujar_oso(self, pantalla, x=OSO_X):
        """El oso, parado sobre el suelo. x es dónde está: se mueve durante el Espíritu del Piso.
        Si no hay imagen, se dibuja una silueta negra con sombrero de mago."""
        x = int(x)
        y = OSO_Y
        if self.imagen_oso is not None:
            ancho = self.imagen_oso.get_width()
            alto = self.imagen_oso.get_height()
            pantalla.blit(self.imagen_oso, (x - ancho // 2, SUELO_Y - alto))   # los pies sobre el suelo
            return
        # cola
        pygame.draw.arc(pantalla, COLOR_OSO, (x + 15, y + 5, 60, 55), -1.2, 1.6, 7)
        # cuerpo y cabeza
        pygame.draw.ellipse(pantalla, COLOR_OSO, (x - 38, y, 76, 62))
        pygame.draw.circle(pantalla, COLOR_OSO, (x, y - 5), 30)
        # orejas
        pygame.draw.polygon(pantalla, COLOR_OSO, [(x - 28, y - 14), (x - 20, y - 46), (x - 6, y - 30)])
        pygame.draw.polygon(pantalla, COLOR_OSO, [(x + 28, y - 14), (x + 20, y - 46), (x + 6, y - 30)])
        # sombrero de mago, torcido
        punta = (x + 12, y - 92)
        pygame.draw.polygon(pantalla, COLOR_SOMBRERO, [(x - 24, y - 30), (x + 22, y - 30), punta])
        pygame.draw.polygon(pantalla, mezclar(COLOR_SOMBRERO, PLATA, 0.35),
                            [(x - 24, y - 30), (x + 22, y - 30), punta], 1)
        pygame.draw.line(pantalla, mezclar(COLOR_SOMBRERO, PLATA, 0.5), (x - 30, y - 30), (x + 28, y - 30), 3)
        k = self.respirar(1.5)
        dibujar_brillo(pantalla, self.brillo_chico, punta, 0.5 + 0.5 * k)
        pygame.draw.circle(pantalla, CIAN_CLARO, punta, 3)
        # ojos
        for dx in (-11, 11):
            dibujar_brillo(pantalla, self.brillo_chico, (x + dx, y - 6), 0.7)
            pygame.draw.ellipse(pantalla, CIAN_CLARO, (x + dx - 4, y - 10, 8, 8))
            pygame.draw.line(pantalla, COLOR_OSO, (x + dx, y - 10), (x + dx, y - 3), 2)

    def dibujar_frente(self, pantalla):
        """Lo que va adelante de todo: la niebla baja y los árboles que se mueven con el viento."""
        self.dibujar_niebla(pantalla, self.niebla_frente, ALTO - 150, -self.niebla_x * 0.6)
        viento = self.viento + math.sin(self.tiempo * 0.02) * 2   # siempre se mueven un poquito
        for arbol in self.arboles_frente:
            for inicio, fin, grosor in arbol["ramas"]:
                a = self.mecer(inicio, arbol, viento)
                b = self.mecer(fin, arbol, viento)
                pygame.draw.line(pantalla, NOCHE_1, a, b, max(1, int(grosor)))
                if grosor > 3:
                    pygame.draw.circle(pantalla, NOCHE_1, (int(b[0]), int(b[1])), int(grosor / 2))

    def mecer(self, punto, arbol, viento):
        """Devuelve el punto corrido por el viento: más arriba, más se mueve."""
        k = (arbol["base_y"] - punto[1]) / arbol["altura"]
        k = max(0, k)
        return (punto[0] + viento * k * k, punto[1])