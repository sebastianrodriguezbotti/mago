# juego.py
# Las reglas de la partida: niveles, fantasmas, hechizos, vidas y puntos.
# Y cómo se dibuja la partida en pantalla.
# main.py solo le pasa la posición de la mano y reproduce los sonidos que esto le pide.

import random
import pygame
import menu
from fantasma import Fantasma
from hechizos import reconocer_simbolo
from escenario import dibujar_trazo, dibujar_cursor, dibujar_brillo
from ajustes import *


# ---------- Reglas ----------

def nueva_partida():
    """Devuelve un diccionario con todo lo que cambia durante una partida."""
    partida = {
        "fantasmas": [],
        "puntos": 0,
        "vidas": VIDAS,
        "nivel": 0,           # posición en la lista NIVELES (0 es el primero)
        "por_salir": 0,       # fantasmas que faltan aparecer en este nivel
        "espera": 0,          # cuadros hasta el próximo fantasma
        "estado": "cartel",   # "cartel", "jugando", "perdiste" o "ganaste"
        "cartel": 0,          # cuadros que le quedan al cartel del nivel
        "trazo": [],          # puntos que se están dibujando con la mano
        "sin_varita": 0,      # cuadros seguidos sin pellizco
    }
    empezar_nivel(partida, 0)
    return partida


def datos_nivel(partida):
    """Devuelve el diccionario del nivel actual, sacado de NIVELES."""
    return NIVELES[partida["nivel"]]


def empezar_nivel(partida, numero):
    """Prepara la partida para el nivel numero, empezando por su cartel."""
    partida["nivel"] = numero
    partida["por_salir"] = NIVELES[numero]["fantasmas"]
    partida["espera"] = NIVELES[numero]["espera"]
    partida["estado"] = "cartel"
    partida["cartel"] = CUADROS_CARTEL
    partida["trazo"] = []


def saltar_cartel(partida):
    """Si se está mostrando el cartel, lo termina ya."""
    if partida["estado"] == "cartel":
        partida["cartel"] = 0


def crear_fantasma(nivel):
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
    return Fantasma(x, y, simbolo, nivel["velocidad"])


def lanzar_hechizo(fantasmas, simbolo):
    """Devuelve la lista de fantasmas que sobreviven al hechizo."""
    sobrevivientes = []
    for f in fantasmas:
        if f.simbolo != simbolo:
            sobrevivientes.append(f)
    return sobrevivientes


def actualizar(partida, pos):
    """Avanza la partida un cuadro. pos es lo que detectó la cámara: (x, y) o None.
    Devuelve la lista de nombres de sonidos que hay que reproducir."""
    sonidos = []

    if partida["estado"] == "cartel":
        partida["cartel"] -= 1
        if partida["cartel"] <= 0:
            partida["estado"] = "jugando"
        return sonidos

    if partida["estado"] != "jugando":
        return sonidos

    nivel = datos_nivel(partida)

    # 1. La mano: sumar puntos al trazo, o terminarlo y lanzar el hechizo
    if pos is not None:
        partida["trazo"].append(pos)
        partida["sin_varita"] = 0
    else:
        partida["sin_varita"] += 1
        if partida["sin_varita"] == CUADROS_SIN_VARITA and len(partida["trazo"]) > 0:
            simbolo = reconocer_simbolo(partida["trazo"])
            partida["trazo"] = []
            if simbolo is not None:
                antes = len(partida["fantasmas"])
                partida["fantasmas"] = lanzar_hechizo(partida["fantasmas"], simbolo)
                eliminados = antes - len(partida["fantasmas"])
                if eliminados > 0:
                    partida["puntos"] += eliminados * PUNTOS_POR_FANTASMA
                    sonidos.append("hechizo")
                else:
                    sonidos.append("fallo")
            else:
                sonidos.append("fallo")

    # 2. Aparecen fantasmas nuevos
    if partida["por_salir"] > 0:
        partida["espera"] -= 1
        if partida["espera"] <= 0:
            partida["fantasmas"].append(crear_fantasma(nivel))
            partida["por_salir"] -= 1
            partida["espera"] = nivel["espera"]

    # 3. Los fantasmas se mueven; si llegan al gato, se pierde una vida
    for f in partida["fantasmas"]:
        f.mover()
    quedan = []
    for f in partida["fantasmas"]:
        if f.choca_con_gato():
            partida["vidas"] -= 1
            sonidos.append("dano")
        else:
            quedan.append(f)
    partida["fantasmas"] = quedan

    # 4. ¿Perdiste, o terminó el nivel?
    if partida["vidas"] <= 0:
        partida["estado"] = "perdiste"
        sonidos.append("fin")
    elif partida["por_salir"] == 0 and len(partida["fantasmas"]) == 0:
        if partida["nivel"] == len(NIVELES) - 1:
            partida["estado"] = "ganaste"
            sonidos.append("fin")
        else:
            empezar_nivel(partida, partida["nivel"] + 1)

    return sonidos


# ---------- Dibujo ----------

def dibujar(pantalla, partida, pos, r):
    """Dibuja la partida. r es un diccionario con los recursos: fuentes, bosque, sprite, velo."""
    bosque = r["bosque"]
    for f in partida["fantasmas"]:
        f.dibujar(pantalla, r["sprite"], bosque.brillo_fuego)

    dibujar_trazo(pantalla, partida["trazo"])
    if pos is not None:
        dibujar_cursor(pantalla, bosque.brillo_chico, pos)

    dibujar_indicadores(pantalla, partida, r)

    if partida["estado"] == "jugando" and partida["sin_varita"] > CUADROS_AVISO:
        menu.escribir(pantalla, r["chica"], "Juntá el índice y el pulgar para dibujar",
                      COLOR_AVISO, (ANCHO // 2, ALTO // 2 - 60))

    if partida["estado"] == "cartel":
        dibujar_cartel(pantalla, partida, r)
    elif partida["estado"] in ("perdiste", "ganaste"):
        dibujar_fin(pantalla, partida, r)


def dibujar_indicadores(pantalla, partida, r):
    """Puntos a la izquierda, vidas como fuegos fatuos, nivel a la derecha."""
    pantalla.blit(r["texto"].render(f"Puntos  {partida['puntos']}", True, COLOR_TEXTO), (24, 16))
    for i in range(partida["vidas"]):
        centro = (36 + i * 30, 76)
        dibujar_brillo(pantalla, r["bosque"].brillo_chico, centro, 1)
        pygame.draw.circle(pantalla, CIAN_CLARO, centro, 4)
    texto = r["texto"].render(f"Nivel  {partida['nivel'] + 1} de {len(NIVELES)}", True, COLOR_TEXTO)
    pantalla.blit(texto, (ANCHO - texto.get_width() - 24, 16))


def dibujar_cartel(pantalla, partida, r):
    """El cartel que presenta cada nivel: número, nombre y qué hay de nuevo."""
    nivel = datos_nivel(partida)
    pantalla.blit(r["velo"], (0, 0))
    menu.escribir_tallado(pantalla, r["titulo"], f"Nivel {partida['nivel'] + 1}", (ANCHO // 2, ALTO // 2 - 110))
    menu.escribir(pantalla, r["subtitulo"], nivel["nombre"], PLATA, (ANCHO // 2, ALTO // 2 - 45))
    menu.separador(pantalla, ALTO // 2 - 5, 320)
    for i in range(len(nivel["novedades"])):
        menu.escribir(pantalla, r["chica"], nivel["novedades"][i], COLOR_TEXTO,
                      (ANCHO // 2, ALTO // 2 + 35 + i * 32))
    menu.escribir_brillante(pantalla, r["chica"], "Enter para empezar ya", (ANCHO // 2, ALTO // 2 + 160))


def dibujar_fin(pantalla, partida, r):
    pantalla.blit(r["velo"], (0, 0))
    if partida["estado"] == "ganaste":
        titulo = "Ganaste"
        frase = "El bosque vuelve a dormir"
    else:
        titulo = "Perdiste"
        frase = "La niebla se llevó al gato"
    menu.escribir_tallado(pantalla, r["titulo"], titulo, (ANCHO // 2, ALTO // 2 - 70))
    menu.escribir(pantalla, r["texto"], frase, PLATA, (ANCHO // 2, ALTO // 2 - 10))
    menu.separador(pantalla, ALTO // 2 + 25, 300)
    menu.escribir(pantalla, r["texto"], f"Puntos  {partida['puntos']}", COLOR_TEXTO, (ANCHO // 2, ALTO // 2 + 60))
    menu.escribir_brillante(pantalla, r["chica"], "R  jugar de nuevo     ·     Esc  volver al menú",
                            (ANCHO // 2, ALTO // 2 + 110))