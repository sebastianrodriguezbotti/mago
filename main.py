# main.py
# El gato mago: dibujá en el aire el sigilo de cada espíritu para espantarlo.
# Este archivo arma todo, maneja las escenas (menú, instrucciones, juego)
# y corre el bucle principal. Las reglas de la partida están en juego.py.

import pygame
import vision
import menu
import juego
from fantasma import crear_sprite_fantasma
import os
from escenario import Bosque, cargar_fuente, cargar_imagen_fondo, dibujar_cursor, mezclar
from ajustes import *


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
pygame.display.set_caption("Noche de Fantasmas")
pygame.mouse.set_visible(False)      # el cursor es un fuego fatuo
reloj = pygame.time.Clock()

sonidos = {
    "hechizo": pygame.mixer.Sound("sonidos/hechizo.wav"),
    "fallo": pygame.mixer.Sound("sonidos/fallo.wav"),
    "dano": pygame.mixer.Sound("sonidos/dano.wav"),
    "fin": pygame.mixer.Sound("sonidos/fin.wav"),
}
volumenes = {"musica": VOLUMEN_MUSICA_INICIAL, "efectos": VOLUMEN_EFECTOS_INICIAL}
menu.aplicar_volumen(sonidos.values(), volumenes["efectos"])

# música de fondo, si hay un archivo
for extension in (".ogg", ".mp3", ".wav"):
    if os.path.exists(MUSICA + extension):
        pygame.mixer.music.load(MUSICA + extension)
        pygame.mixer.music.play(-1)      # -1: se repite para siempre
        break
pygame.mixer.music.set_volume(volumenes["musica"])

cap = vision.abrir_camara()
if cap is None:
    print("No se pudo abrir la cámara. Probá cambiar CAMARA_INDICE en ajustes.py")
    pygame.quit()
    raise SystemExit

bosque = Bosque()
fondo_menu = cargar_imagen_fondo(IMAGEN_FONDO_MENU)   # None si no está la imagen

# velos oscuros: para los carteles y para los fundidos a negro
velo = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
velo.fill((*NOCHE_1, 170))
negro = pygame.Surface((ANCHO, ALTO))
negro.fill(NOCHE_1)

# todo lo que juego.py necesita para dibujar, en un solo diccionario
recursos = {
    "bosque": bosque,
    "sprite": crear_sprite_fantasma(),
    "velo": velo,
    "titulo": cargar_fuente(FUENTE_TITULO, 70),
    "subtitulo": cargar_fuente(FUENTE_TITULO, 36),
    "texto": cargar_fuente(FUENTE_TEXTO, 26),
    "chica": cargar_fuente(FUENTE_TEXTO, 18),
}
recursos["titulo_juego"] = menu.crear_titulo(cargar_fuente(FUENTE_TITULO, TITULO_TAMANO))
fuente_menu = cargar_fuente(FUENTE_TEXTO, TAMANO_MENU)
sombra_izquierda = menu.crear_sombra_izquierda()
fuente = recursos["texto"]

escena = "menu"     # "menu", "instrucciones", "sonido" o "juego"
seleccion = 0       # opción marcada en el menú
seleccion_sonido = 0  # opción marcada en "Música y sonido"
destino = None      # a qué escena vamos cuando hay un fundido; None si no hay
fundido = 255       # 0 = se ve todo, 255 = todo negro. Arranca en negro y aparece.
partida = juego.nueva_partida()
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
            seleccion, eleccion = menu.evento_menu(e, fuente_menu, seleccion)
            if eleccion == "Jugar":
                destino = "juego"
            elif eleccion == "Cómo jugar":
                destino = "instrucciones"
            elif eleccion == "Música y sonido":
                destino = "sonido"
                seleccion_sonido = 0
            elif eleccion == "Salir":
                destino = "salir"

        elif escena == "sonido":
            seleccion_sonido, que_paso = menu.evento_sonido(e, fuente_menu, seleccion_sonido, volumenes)
            if que_paso == "cambio":
                pygame.mixer.music.set_volume(volumenes["musica"])
                menu.aplicar_volumen(sonidos.values(), volumenes["efectos"])
                sonidos["hechizo"].play()    # para escuchar cómo quedó
            elif que_paso == "volver":
                destino = "menu"

        elif escena == "instrucciones":
            if menu.evento_instrucciones(e, fuente_menu) == "volver":
                destino = "menu"

        elif escena == "juego" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                destino = "menu"
            elif e.key == pygame.K_RETURN:
                juego.saltar_cartel(partida)
            elif e.key == pygame.K_r and partida["estado"] in ("perdiste", "ganaste"):
                destino = "juego"

    # --- Fundido a negro entre escenas ---
    if destino is not None:
        fundido = min(255, fundido + VELOCIDAD_FUNDIDO)
        if fundido == 255:
            # ya está todo negro: recién ahora se cambia de escena
            if destino == "salir":
                andando = False
            elif destino == "juego":
                partida = juego.nueva_partida()
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
    if escena == "juego":
        for nombre in juego.actualizar(partida, pos):
            sonidos[nombre].play()

    # --- Dibujar ---
    # de atrás hacia adelante: lo que se dibuja después queda encima
    if escena != "juego" and fondo_menu is not None:
        pantalla.blit(fondo_menu, (0, 0))      # las pantallas del menú usan la imagen
    else:
        bosque.dibujar_fondo(pantalla)
        bosque.dibujar_piedras(pantalla, False)
        bosque.dibujar_gato(pantalla)
        bosque.dibujar_piedras(pantalla, True)
        bosque.dibujar_frente(pantalla)

    if escena == "menu":
        menu.dibujar_menu(pantalla, recursos["titulo_juego"], fuente_menu, recursos["chica"], seleccion)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())
    elif escena == "sonido":
        menu.dibujar_sonido(pantalla, recursos["titulo_juego"], fuente_menu, recursos["chica"],
                            seleccion_sonido, volumenes)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())
    elif escena == "instrucciones":
        menu.dibujar_instrucciones(pantalla, recursos["titulo"], fuente_menu, recursos["chica"], sombra_izquierda)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())
    elif escena == "juego":
        juego.dibujar(pantalla, partida, pos, recursos)
        if frame is not None:
            dibujar_espejo(pantalla, frame, pos)

    if fundido > 0:
        negro.set_alpha(fundido)
        pantalla.blit(negro, (0, 0))

    pygame.display.flip()
    reloj.tick(FPS)

cap.release()
pygame.quit()