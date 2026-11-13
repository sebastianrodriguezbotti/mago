# main.py
# El gato mago: dibujá en el aire el sigilo de cada espíritu para espantarlo.

import random
import pygame
import vision
import menu
from hechizos import reconocer_simbolo
from fantasma import Fantasma, crear_sprite_fantasma
from escenario import Bosque, cargar_fuente, dibujar_trazo, dibujar_cursor, dibujar_brillo, mezclar
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


def dibujar_espejo(pantalla, frame, pos):
    """La cámara chiquita en la esquina, con marco de plata."""
    chico = vision.cuadro_espejo(frame)
    sup = pygame.image.frombuffer(chico.tobytes(), (ESPEJO_ANCHO, ESPEJO_ALTO), "BGR")
    x = ANCHO - ESPEJO_ANCHO - ESPEJO_MARGEN
    y = ALTO - ESPEJO_ALTO - ESPEJO_MARGEN
    pantalla.blit(sup, (x, y))
    marco = pygame.Rect(x, y, ESPEJO_ANCHO, ESPEJO_ALTO)
    pygame.draw.rect(pantalla, PLATA, marco, 1)
    pygame.draw.rect(pantalla, mezclar(NOCHE_1, PLATA, 0.4), marco.inflate(8, 8), 1)
    # dónde está la varita, también en el espejo
    if pos is not None:
        px = x + pos[0] * ESPEJO_ANCHO // ANCHO
        py = y + pos[1] * ESPEJO_ALTO // ALTO
        pygame.draw.circle(pantalla, CIAN_CLARO, (px, py), 4)


# ---------- Preparación (todo se carga una sola vez, antes del bucle) ----------

pygame.init()
pygame.mixer.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("El gato mago")
pygame.mouse.set_visible(False)      # el cursor es un fuego fatuo
reloj = pygame.time.Clock()

fuente_titulo = cargar_fuente(FUENTE_TITULO, 62)
fuente_subtitulo = cargar_fuente(FUENTE_TITULO, 34)
fuente = cargar_fuente(FUENTE_TEXTO, 36)
fuente_chica = cargar_fuente(FUENTE_TEXTO, 25)

sonido_hechizo = pygame.mixer.Sound("sonidos/hechizo.wav")
sonido_fallo = pygame.mixer.Sound("sonidos/fallo.wav")
sonido_dano = pygame.mixer.Sound("sonidos/dano.wav")
sonido_fin = pygame.mixer.Sound("sonidos/fin.wav")
sonidos = [sonido_hechizo, sonido_fallo, sonido_dano, sonido_fin]

volumen = VOLUMEN_INICIAL
menu.aplicar_volumen(sonidos, volumen)

cap = vision.abrir_camara()
if cap is None:
    print("No se pudo abrir la cámara. Probá cambiar CAMARA_INDICE en ajustes.py")
    pygame.quit()
    raise SystemExit

bosque = Bosque()
sprite_fantasma = crear_sprite_fantasma()

# velos oscuros: para el fin de partida y para los fundidos a negro
velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
velo.fill((*NOCHE_1, 170))
negro = pygame.Surface((ANCHO, ALTO))
negro.fill(NOCHE_1)

escena = "menu"     # "menu", "instrucciones" o "juego"
seleccion = 0       # opción marcada en el menú
destino = None      # a qué escena vamos cuando hay un fundido; None si no hay
fundido = 255       # 0 = se ve todo, 255 = todo negro. Arranca en negro y aparece.
partida = nueva_partida()
trazo = []          # puntos que se están dibujando con la mano
sin_varita = 0      # cuadros seguidos sin pellizco
pos = None


# ---------- Bucle principal ----------

andando = True
while andando:

    # --- Eventos ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            andando = False

        if destino is not None:
            continue            # durante un fundido no se aceptan teclas

        if escena == "menu":
            elegir = False
            if e.type == pygame.MOUSEMOTION:
                debajo = menu.opcion_bajo_mouse(fuente, e.pos, volumen)
                if debajo is not None:
                    seleccion = debajo
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                debajo = menu.opcion_bajo_mouse(fuente, e.pos, volumen)
                if debajo is not None:
                    seleccion = debajo
                    if menu.OPCIONES[seleccion] == "Volumen":
                        # clic a la izquierda baja, a la derecha sube
                        if e.pos[0] < ANCHO // 2:
                            volumen = menu.cambiar_volumen(volumen, -1)
                        else:
                            volumen = menu.cambiar_volumen(volumen, 1)
                        menu.aplicar_volumen(sonidos, volumen)
                        sonido_hechizo.play()
                    else:
                        elegir = True
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    destino = "salir"
                elif e.key == pygame.K_UP:
                    seleccion = (seleccion - 1) % len(menu.OPCIONES)
                elif e.key == pygame.K_DOWN:
                    seleccion = (seleccion + 1) % len(menu.OPCIONES)
                elif menu.OPCIONES[seleccion] == "Volumen" and e.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    if e.key == pygame.K_LEFT:
                        volumen = menu.cambiar_volumen(volumen, -1)
                    else:
                        volumen = menu.cambiar_volumen(volumen, 1)
                    menu.aplicar_volumen(sonidos, volumen)
                    sonido_hechizo.play()    # para escuchar cómo quedó
                elif e.key == pygame.K_RETURN:
                    elegir = True

            if elegir:
                opcion = menu.OPCIONES[seleccion]
                if opcion == "Jugar":
                    destino = "juego"
                elif opcion == "Instrucciones":
                    destino = "instrucciones"
                elif opcion == "Salir":
                    destino = "salir"

        elif escena == "instrucciones":
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                destino = "menu"
            elif e.type == pygame.MOUSEBUTTONDOWN:
                destino = "menu"

        elif escena == "juego" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                destino = "menu"
            elif e.key == pygame.K_r and partida["estado"] != "jugando":
                destino = "juego"

    # --- Fundido a negro entre escenas ---
    if destino is not None:
        fundido = min(255, fundido + VELOCIDAD_FUNDIDO)
        if fundido == 255:
            # ya está todo negro: recién ahora se cambia de escena
            if destino == "salir":
                andando = False
            elif destino == "juego":
                partida = nueva_partida()
                trazo = []
                sin_varita = 0
            escena = destino
            destino = None
    elif fundido > 0:
        fundido = max(0, fundido - VELOCIDAD_FUNDIDO)

    # --- Cámara ---
    frame = vision.leer_cuadro(cap)
    if frame is not None and escena == "juego":
        pos = vision.detectar_mano(frame)
    else:
        pos = None

    # --- Actualizar ---
    bosque.actualizar()

    if escena == "juego" and partida["estado"] == "jugando":

        # 1. La mano: sumar puntos al trazo, o terminarlo
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
    # de atrás hacia adelante: lo que se dibuja después queda encima
    bosque.dibujar_fondo(pantalla)
    bosque.dibujar_piedras(pantalla, False)
    bosque.dibujar_gato(pantalla)
    bosque.dibujar_piedras(pantalla, True)

    if escena == "juego":
        for f in partida["fantasmas"]:
            f.dibujar(pantalla, sprite_fantasma, bosque.brillo_fuego)

    bosque.dibujar_frente(pantalla)

    if escena == "menu":
        menu.dibujar_menu(pantalla, fuente_titulo, fuente, fuente_chica, seleccion, volumen)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())

    elif escena == "instrucciones":
        menu.dibujar_instrucciones(pantalla, fuente_subtitulo, fuente, fuente_chica)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())

    else:
        dibujar_trazo(pantalla, trazo)
        if pos is not None:
            dibujar_cursor(pantalla, bosque.brillo_chico, pos)

        # indicadores: puntos a la izquierda, vidas como fuegos fatuos, oleada a la derecha
        pantalla.blit(fuente.render(f"Puntos  {partida['puntos']}", True, COLOR_TEXTO), (24, 16))
        for i in range(partida["vidas"]):
            centro = (36 + i * 30, 76)
            dibujar_brillo(pantalla, bosque.brillo_chico, centro, 1)
            pygame.draw.circle(pantalla, CIAN_CLARO, centro, 4)
        texto = fuente.render(f"Oleada  {partida['oleada']} de {OLEADAS_PARA_GANAR}", True, COLOR_TEXTO)
        pantalla.blit(texto, (ANCHO - texto.get_width() - 24, 16))

        if frame is not None:
            dibujar_espejo(pantalla, frame, pos)

        if partida["estado"] == "jugando" and sin_varita > CUADROS_AVISO:
            menu.escribir(pantalla, fuente_chica, "Juntá el índice y el pulgar para dibujar",
                          COLOR_AVISO, (ANCHO // 2, ALTO // 2 - 60))

        if partida["estado"] != "jugando":
            pantalla.blit(velo, (0, 0))
            if partida["estado"] == "ganaste":
                titulo = "Ganaste"
                frase = "El bosque vuelve a dormir"
            else:
                titulo = "Perdiste"
                frase = "La niebla se llevó al gato"
            menu.escribir_tallado(pantalla, fuente_titulo, titulo, (ANCHO // 2, ALTO // 2 - 70))
            menu.escribir(pantalla, fuente, frase, PLATA, (ANCHO // 2, ALTO // 2 - 10))
            menu.separador(pantalla, ALTO // 2 + 25, 300)
            menu.escribir(pantalla, fuente, f"Puntos  {partida['puntos']}", COLOR_TEXTO, (ANCHO // 2, ALTO // 2 + 60))
            menu.escribir_brillante(pantalla, fuente_chica, "R  jugar de nuevo     ·     Esc  volver al menú",
                                    (ANCHO // 2, ALTO // 2 + 110))

    if fundido > 0:
        negro.set_alpha(fundido)
        pantalla.blit(negro, (0, 0))

    pygame.display.flip()
    reloj.tick(FPS)

cap.release()
pygame.quit()