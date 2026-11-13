# main.py
# El gato mago: dibujá en el aire el símbolo de cada fantasma para eliminarlo.

import random
import pygame
import vision
from hechizos import reconocer_simbolo
from fantasma import Fantasma
from ajustes import *


# ---------- Funciones ----------

def nueva_partida():
    """Devuelve un diccionario con todo lo que cambia durante una partida."""
    return {
        "fantasmas": [],
        "puntos": 0,
        "vidas": VIDAS,
        "oleada": 1,
        "por_salir": FANTASMAS_POR_OLEADA,   # fantasmas que faltan aparecer en esta oleada
        "espera": CUADROS_ENTRE_FANTASMAS,   # cuadros hasta el próximo fantasma
        "estado": "jugando",                 # "jugando", "perdiste" o "ganaste"
    }


def crear_fantasma(oleada):
    """Crea un fantasma en un borde de la pantalla, con un símbolo al azar."""
    borde = random.choice(["arriba", "izquierda", "derecha"])
    if borde == "arriba":
        x = random.randint(RADIO_FANTASMA, ANCHO - RADIO_FANTASMA)
        y = -RADIO_FANTASMA
    elif borde == "izquierda":
        x = -RADIO_FANTASMA
        y = random.randint(0, ALTO // 2)
    else:
        x = ANCHO + RADIO_FANTASMA
        y = random.randint(0, ALTO // 2)
    simbolo = random.choice(SIMBOLOS)
    velocidad = VELOCIDAD_FANTASMA + (oleada - 1) * AUMENTO_VELOCIDAD
    return Fantasma(x, y, simbolo, velocidad)


def lanzar_hechizo(fantasmas, simbolo):
    """Devuelve la lista de fantasmas que sobreviven al hechizo."""
    sobrevivientes = []
    for f in fantasmas:
        if f.simbolo != simbolo:
            sobrevivientes.append(f)
    return sobrevivientes


def dibujar_gato(pantalla):
    # cuerpo y cabeza
    pygame.draw.ellipse(pantalla, COLOR_GATO, (GATO_X - 35, GATO_Y, 70, 60))
    pygame.draw.circle(pantalla, COLOR_GATO, (GATO_X, GATO_Y - 5), 28)
    # orejas
    pygame.draw.polygon(pantalla, COLOR_GATO,
                        [(GATO_X - 26, GATO_Y - 15), (GATO_X - 18, GATO_Y - 42), (GATO_X - 6, GATO_Y - 28)])
    pygame.draw.polygon(pantalla, COLOR_GATO,
                        [(GATO_X + 26, GATO_Y - 15), (GATO_X + 18, GATO_Y - 42), (GATO_X + 6, GATO_Y - 28)])
    # sombrero de mago
    pygame.draw.polygon(pantalla, COLOR_SOMBRERO,
                        [(GATO_X - 20, GATO_Y - 30), (GATO_X + 20, GATO_Y - 30), (GATO_X + 5, GATO_Y - 80)])
    # ojos
    pygame.draw.circle(pantalla, COLOR_SIMBOLO, (GATO_X - 10, GATO_Y - 6), 5)
    pygame.draw.circle(pantalla, COLOR_SIMBOLO, (GATO_X + 10, GATO_Y - 6), 5)


def escribir(pantalla, fuente, texto, color, centro):
    sup = fuente.render(texto, True, color)
    rect = sup.get_rect(center=centro)
    pantalla.blit(sup, rect)


# ---------- Preparación (todo se carga una sola vez, antes del bucle) ----------

pygame.init()
pygame.mixer.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El gato mago")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 32)
fuente_grande = pygame.font.SysFont(None, 64)

sonido_hechizo = pygame.mixer.Sound("sonidos/hechizo.wav")
sonido_fallo = pygame.mixer.Sound("sonidos/fallo.wav")
sonido_dano = pygame.mixer.Sound("sonidos/dano.wav")
sonido_fin = pygame.mixer.Sound("sonidos/fin.wav")

cap = vision.abrir_camara()
if cap is None:
    print("No se pudo abrir la cámara. Probá cambiar CAMARA_INDICE en ajustes.py")
    pygame.quit()
    raise SystemExit

# capa negra semitransparente para oscurecer la cámara de fondo
sombra = pygame.Surface((ANCHO, ALTO))
sombra.fill((0, 0, 0))
sombra.set_alpha(130)

partida = nueva_partida()
trazo = []          # puntos que se están dibujando con la varita
sin_varita = 0      # cuadros seguidos sin ver la varita
pos = None


# ---------- Bucle principal ----------

andando = True
while andando:

    # --- Eventos ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            andando = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
            if partida["estado"] != "jugando":
                partida = nueva_partida()
                trazo = []

    # --- Cámara ---
    frame = vision.leer_cuadro(cap)
    if frame is not None:
        pos = vision.detectar_varita(frame)
    else:
        pos = None

    # --- Actualizar ---
    if partida["estado"] == "jugando":

        # 1. La varita: sumar puntos al trazo, o terminarlo
        if pos is not None:
            trazo.append(pos)
            sin_varita = 0
        else:
            sin_varita += 1
            if sin_varita == CUADROS_SIN_VARITA and len(trazo) > 0:
                simbolo = reconocer_simbolo(trazo)
                trazo = []
                if simbolo is not None:
                    antes = len(partida["fantasmas"])
                    partida["fantasmas"] = lanzar_hechizo(partida["fantasmas"], simbolo)
                    eliminados = antes - len(partida["fantasmas"])
                    if eliminados > 0:
                        partida["puntos"] += eliminados * PUNTOS_POR_FANTASMA
                        sonido_hechizo.play()
                    else:
                        sonido_fallo.play()
                else:
                    sonido_fallo.play()

        # 2. Aparecen fantasmas nuevos
        if partida["por_salir"] > 0:
            partida["espera"] -= 1
            if partida["espera"] <= 0:
                partida["fantasmas"].append(crear_fantasma(partida["oleada"]))
                partida["por_salir"] -= 1
                partida["espera"] = CUADROS_ENTRE_FANTASMAS

        # 3. Los fantasmas se mueven; si llegan al gato, se pierde una vida
        for f in partida["fantasmas"]:
            f.mover()
        quedan = []
        for f in partida["fantasmas"]:
            if f.choca_con_gato():
                partida["vidas"] -= 1
                sonido_dano.play()
            else:
                quedan.append(f)
        partida["fantasmas"] = quedan

        # 4. ¿Perdiste, terminó la oleada o ganaste?
        if partida["vidas"] <= 0:
            partida["estado"] = "perdiste"
            sonido_fin.play()
        elif partida["por_salir"] == 0 and len(partida["fantasmas"]) == 0:
            if partida["oleada"] == OLEADAS_PARA_GANAR:
                partida["estado"] = "ganaste"
                sonido_fin.play()
            else:
                partida["oleada"] += 1
                partida["por_salir"] = FANTASMAS_POR_OLEADA
                partida["espera"] = CUADROS_ENTRE_FANTASMAS

    # --- Dibujar ---
    if frame is not None:
        sup = pygame.image.frombuffer(frame.tobytes(), (ANCHO, ALTO), "BGR")
        pantalla.blit(sup, (0, 0))
    else:
        pantalla.fill((0, 0, 0))
    pantalla.blit(sombra, (0, 0))

    dibujar_gato(pantalla)
    for f in partida["fantasmas"]:
        f.dibujar(pantalla)

    if len(trazo) >= 2:
        pygame.draw.lines(pantalla, COLOR_TRAZO, False, trazo, 6)
    if pos is not None:
        pygame.draw.circle(pantalla, COLOR_TRAZO, pos, 12, 3)

    # indicadores
    info = f"Puntos: {partida['puntos']}   Vidas: {partida['vidas']}   Oleada: {partida['oleada']}/{OLEADAS_PARA_GANAR}"
    pantalla.blit(fuente.render(info, True, COLOR_TEXTO), (10, 10))

    if partida["estado"] == "jugando" and sin_varita > CUADROS_AVISO:
        escribir(pantalla, fuente, "Mostrá la varita a la cámara", COLOR_AVISO, (ANCHO // 2, ALTO // 2))

    if partida["estado"] != "jugando":
        if partida["estado"] == "ganaste":
            titulo = "¡Ganaste!"
        else:
            titulo = "Perdiste"
        escribir(pantalla, fuente_grande, titulo, COLOR_TEXTO, (ANCHO // 2, ALTO // 2 - 30))
        escribir(pantalla, fuente, f"Puntos: {partida['puntos']}  -  Apretá R para jugar de nuevo",
                 COLOR_TEXTO, (ANCHO // 2, ALTO // 2 + 20))

    pygame.display.flip()
    reloj.tick(FPS)

cap.release()
pygame.quit()