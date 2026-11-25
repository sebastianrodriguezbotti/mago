# juego.py
# Las reglas de la partida: niveles, fantasmas, hechizos, la vida del oso y el jefe.
# Y cómo se dibuja la partida en pantalla.
# main.py solo le pasa la posición de la mano y reproduce los sonidos que esto le pide.

import random
import pygame
import menu
from fantasma import Fantasma
from espiritu_piso import EspirituDelPiso
from hechizos import reconocer_simbolo
from escenario import dibujar_trazo, dibujar_cursor, dibujar_brillo, mezclar
from ajustes import *


# ---------- Reglas ----------

def nueva_partida(nivel_inicio=0):
    """Devuelve un diccionario con todo lo que cambia durante una partida,
    empezando en el nivel nivel_inicio (0 es el primero)."""
    partida = {
        "fantasmas": [],
        "vida": VIDA_OSO,    # la barra del oso: si llega a 0, perdés
        "nivel": 0,           # posición en la lista NIVELES (0 es el primero)
        "por_salir": 0,       # fantasmas que faltan aparecer en este nivel
        "espera": 0,          # cuadros hasta el próximo fantasma
        "estado": "cartel",   # "cartel", "jugando", "perdiste" o "ganaste"
        "cartel": 0,          # cuadros que le quedan al cartel del nivel
        "trazo": [],          # puntos que se están dibujando con la mano
        "sin_varita": 0,      # cuadros seguidos sin pellizco
        "inicio": nivel_inicio,   # para "jugar de nuevo" desde el mismo nivel
        "completado": None,   # cuando se supera un nivel, queda su número hasta que main lo guarda
        "oso_x": OSO_X,     # el oso se mueve solo durante el Espíritu del Piso
        "espiritu": None,     # el Espíritu del Piso, cuando está afuera
        "hasta_espiritu": 0,  # cuadros hasta que salga el próximo
        "sin_cara": 0,        # cuadros seguidos sin ver la cara
    }
    empezar_nivel(partida, nivel_inicio)
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
    partida["vida"] = VIDA_OSO          # cada nivel empieza con la vida llena
    partida["oso_x"] = OSO_X
    partida["hasta_espiritu"] = ESPIRITU_PRIMERA_VEZ
    if es_nivel_jefe(partida):
        # el jefe está desde el principio y dura todo el nivel
        partida["espiritu"] = EspirituDelPiso(NIVELES[numero]["ataques_piso"], jefe=True)
    else:
        partida["espiritu"] = None


def es_nivel_jefe(partida):
    """Devuelve True si el nivel actual es el del jefe."""
    return datos_nivel(partida).get("jefe", False)


def saltar_cartel(partida):
    """Si se está mostrando el cartel, lo termina ya."""
    if partida["estado"] == "cartel":
        partida["cartel"] = 0


def usa_cabeza(partida):
    """Devuelve True si ahora la cámara tiene que buscar la cara (para esquivar)
    en vez de la mano (para dibujar)."""
    espiritu = partida["espiritu"]
    if espiritu is None or partida["estado"] != "jugando":
        return False
    return espiritu.fase in ("subiendo", "atacando")


def leer_trazo(partida, pos):
    """La mano: suma el punto al trazo, o, si se soltó el pellizco, lo termina.
    Devuelve el símbolo dibujado cuando se termina un trazo ("" si no se reconoció),
    o None si el trazo sigue o no hay trazo."""
    if pos is not None:
        partida["trazo"].append(pos)
        partida["sin_varita"] = 0
        return None
    partida["sin_varita"] += 1
    if partida["sin_varita"] == CUADROS_SIN_VARITA and len(partida["trazo"]) > 0:
        simbolo = reconocer_simbolo(partida["trazo"])
        partida["trazo"] = []
        if simbolo is None:
            return ""
        return simbolo
    return None


def herir_oso(partida, dano):
    """Le saca vida al oso, sin bajar de 0."""
    partida["vida"] = max(0, partida["vida"] - dano)


def mover_oso(partida, cara):
    """Mueve el oso hacia donde apunta la cabeza. Si no se ve la cara, se queda quieto."""
    if cara is None:
        partida["sin_cara"] += 1
        return
    partida["sin_cara"] = 0
    # la cabeza se mueve poco: se exagera la distancia al centro
    objetivo = ANCHO / 2 + (cara[0] - ANCHO / 2) * SENSIBILIDAD_CABEZA
    objetivo = max(MARGEN_OSO, min(ANCHO - MARGEN_OSO, objetivo))
    partida["oso_x"] += (objetivo - partida["oso_x"]) * SUAVIDAD_OSO


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
    espiritu = partida["espiritu"]

    if espiritu is not None and espiritu.fase == "vulnerable":
        # --- El jefe está descubierto: se lo daña dibujando su sigilo con la mano ---
        simbolo = leer_trazo(partida, pos)
        if simbolo is not None:
            if espiritu.recibir_hechizo(simbolo):
                sonidos.append("hechizo")
            else:
                sonidos.append("fallo")
        espiritu.actualizar(partida["oso_x"])
        partida["oso_x"] += (OSO_X - partida["oso_x"]) * 0.1

    elif espiritu is not None:
        # --- Espíritu del Piso atacando: los fantasmas se quedan quietos y hay que esquivar ---
        mover_oso(partida, pos)
        resultado = espiritu.actualizar(partida["oso_x"])
        if resultado == "dano":
            herir_oso(partida, DANO_GARRA)
            sonidos.append("dano")
        elif resultado == "golpe":
            sonidos.append("fallo")
        if espiritu.fase == "terminado":
            partida["espiritu"] = None
            partida["hasta_espiritu"] = ESPIRITU_CADA
            sonidos.append("hechizo")

    else:
        # el oso vuelve despacio al centro del círculo
        partida["oso_x"] += (OSO_X - partida["oso_x"]) * 0.1

        # 1. La mano: dibujar y lanzar hechizos
        simbolo = leer_trazo(partida, pos)
        if simbolo is not None:
            antes = len(partida["fantasmas"])
            if simbolo != "":
                partida["fantasmas"] = lanzar_hechizo(partida["fantasmas"], simbolo)
            if len(partida["fantasmas"]) < antes:
                sonidos.append("hechizo")
            else:
                sonidos.append("fallo")

        # 2. Aparecen fantasmas nuevos
        if partida["por_salir"] > 0:
            partida["espera"] -= 1
            if partida["espera"] <= 0:
                partida["fantasmas"].append(crear_fantasma(nivel))
                partida["por_salir"] -= 1
                partida["espera"] = nivel["espera"]

        # 3. Los fantasmas se mueven; si llegan al oso, le sacan vida
        for f in partida["fantasmas"]:
            f.mover()
        quedan = []
        for f in partida["fantasmas"]:
            if f.choca_con_oso():
                herir_oso(partida, DANO_FANTASMA)
                sonidos.append("dano")
            else:
                quedan.append(f)
        partida["fantasmas"] = quedan

        # 4. ¿Le toca salir al Espíritu del Piso?
        if nivel["ataques_piso"] > 0:
            partida["hasta_espiritu"] -= 1
            if partida["hasta_espiritu"] <= 0:
                partida["espiritu"] = EspirituDelPiso(nivel["ataques_piso"])
                partida["trazo"] = []
                partida["sin_cara"] = 0
                sonidos.append("temblor")

    # 5. ¿Perdiste, o terminó el nivel?
    if partida["vida"] <= 0:
        partida["estado"] = "perdiste"
        sonidos.append("fin")
    elif partida["por_salir"] == 0 and len(partida["fantasmas"]) == 0 and partida["espiritu"] is None:
        partida["completado"] = partida["nivel"]
        sonidos.append("nivel")
        if partida["nivel"] == len(NIVELES) - 1:
            partida["estado"] = "ganaste"
            sonidos.append("fin")
        else:
            empezar_nivel(partida, partida["nivel"] + 1)

    return sonidos


# ---------- Dibujo ----------

def dibujar_gigante(pantalla, partida, r):
    """El Espíritu del Piso asomando. Va entre el cielo y el piso."""
    if partida["espiritu"] is not None:
        partida["espiritu"].dibujar_gigante(pantalla, r["bosque"].brillo_fuego)


def dibujar_ataque(pantalla, partida, r):
    """La marca y la garra del Espíritu del Piso. Va encima del oso."""
    if partida["espiritu"] is not None:
        partida["espiritu"].dibujar_ataque(pantalla, r["bosque"].brillo_fuego)


def dibujar_fantasmas(pantalla, partida, r):
    """Dibuja los fantasmas. r es un diccionario con los recursos: fuentes, bosque, sprite, velo."""
    for f in partida["fantasmas"]:
        f.dibujar(pantalla, r["sprite"], r["bosque"].brillo_fuego)


def dibujar_interfaz(pantalla, partida, pos, r, completa=True):
    """Dibuja lo que va encima de todo: el trazo, el cursor, los indicadores y los carteles.
    Con completa=False (en la pausa) dibuja solo los indicadores."""
    bosque = r["bosque"]
    if not completa:
        dibujar_indicadores(pantalla, partida, r)
        return

    espiritu = partida["espiritu"]
    if espiritu is not None:
        espiritu.dibujar_sigilo(pantalla, bosque.brillo_fuego)

    dibujar_trazo(pantalla, partida["trazo"])
    if pos is not None and not usa_cabeza(partida):
        dibujar_cursor(pantalla, bosque.brillo_chico, pos)

    dibujar_indicadores(pantalla, partida, r)

    if espiritu is not None and espiritu.fase == "vulnerable" and partida["estado"] == "jugando":
        menu.escribir_brillante(pantalla, r["texto"], "¡Se descubrió! Dibujá su sigilo con la mano",
                                (ANCHO // 2, ALTO - 30))
    elif usa_cabeza(partida):
        if partida["sin_cara"] > 30:
            menu.escribir_brillante(pantalla, r["texto"], "No veo tu cara: ponete frente a la cámara",
                                    (ANCHO // 2, 130))
        elif espiritu.fase == "subiendo":
            menu.escribir_brillante(pantalla, r["texto"], "¡Algo sube del piso! Mové la cabeza para esquivar",
                                    (ANCHO // 2, 130))
    elif partida["estado"] == "jugando" and partida["sin_varita"] > CUADROS_AVISO:
        menu.escribir(pantalla, r["chica"], "Juntá el índice y el pulgar para dibujar",
                      COLOR_AVISO, (ANCHO // 2, ALTO // 2 - 60))

    if partida["estado"] == "cartel":
        dibujar_cartel(pantalla, partida, r)
    elif partida["estado"] in ("perdiste", "ganaste"):
        dibujar_fin(pantalla, partida, r)


def dibujar_barra_vida(pantalla, x, y, ancho, alto, valor, maximo, titila):
    """Una barra de vida: marco fino de plata y relleno cian según valor/maximo.
    Si titila es True, el relleno parpadea (para avisar que queda poca)."""
    pygame.draw.rect(pantalla, NOCHE_1, (x, y, ancho, alto))
    lleno = int((ancho - 4) * valor / maximo)
    color = CIAN
    if titila and pygame.time.get_ticks() // 200 % 2 == 0:
        color = CIAN_CLARO
    if lleno > 0:
        pygame.draw.rect(pantalla, mezclar(NOCHE_2, color, 0.45), (x + 2, y + 2, lleno, alto - 4))
        pygame.draw.rect(pantalla, color, (x + 2, y + 2, lleno, (alto - 4) // 2))   # brillo arriba
    pygame.draw.rect(pantalla, PLATA, (x, y, ancho, alto), 1)


def dibujar_indicadores(pantalla, partida, r):
    """Vida del oso arriba a la izquierda, nivel a la derecha y, si está el jefe, su vida arriba al centro."""
    menu.escribir(pantalla, r["chica"], "OSO", BLANCO, (24, 24), "midleft")
    poca = partida["vida"] <= VIDA_OSO * 0.3
    dibujar_barra_vida(pantalla, 24, 38, 260, 16, partida["vida"], VIDA_OSO, poca)

    texto = r["texto"].render(f"Nivel  {partida['nivel'] + 1} de {len(NIVELES)}", True, COLOR_TEXTO)
    pantalla.blit(texto, (ANCHO - texto.get_width() - 24, 16))

    espiritu = partida["espiritu"]
    if espiritu is not None and espiritu.jefe:
        menu.escribir(pantalla, r["chica"], JEFE_NOMBRE, BLANCO, (ANCHO // 2, 24))
        dibujar_barra_vida(pantalla, (ANCHO - BARRA_JEFE_ANCHO) // 2, 38, BARRA_JEFE_ANCHO, 16,
                           espiritu.vida, JEFE_VIDA, False)


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
        frase = "La niebla se llevó al oso"
    menu.escribir_tallado(pantalla, r["titulo"], titulo, (ANCHO // 2, ALTO // 2 - 70))
    menu.escribir(pantalla, r["texto"], frase, PLATA, (ANCHO // 2, ALTO // 2 - 10))
    menu.separador(pantalla, ALTO // 2 + 25, 300)
    menu.escribir_brillante(pantalla, r["chica"], "R  jugar de nuevo     ·     Esc  volver al menú",
                            (ANCHO // 2, ALTO // 2 + 70))