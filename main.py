# main.py
# El gato mago: dibujá en el aire el sigilo de cada espíritu para espantarlo.
# Este archivo arma todo, maneja las escenas (menú, instrucciones, juego)
# y corre el bucle principal. Las reglas de la partida están en juego.py.

import pygame
import vision
import menu
import juego
from fantasma import crear_sprite_fantasma
from escenario import Bosque, cargar_fuente, dibujar_cursor, mezclar
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
pygame.display.set_caption("El gato mago")
pygame.mouse.set_visible(False)      # el cursor es un fuego fatuo
reloj = pygame.time.Clock()

sonidos = {
    "hechizo": pygame.mixer.Sound("sonidos/hechizo.wav"),
    "fallo": pygame.mixer.Sound("sonidos/fallo.wav"),
    "dano": pygame.mixer.Sound("sonidos/dano.wav"),
    "fin": pygame.mixer.Sound("sonidos/fin.wav"),
}
volumen = VOLUMEN_INICIAL
menu.aplicar_volumen(sonidos.values(), volumen)

cap = vision.abrir_camara()
if cap is None:
    print("No se pudo abrir la cámara. Probá cambiar CAMARA_INDICE en ajustes.py")
    pygame.quit()
    raise SystemExit

bosque = Bosque()

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
    "titulo": cargar_fuente(FUENTE_TITULO, 62),
    "subtitulo": cargar_fuente(FUENTE_TITULO, 34),
    "texto": cargar_fuente(FUENTE_TEXTO, 36),
    "chica": cargar_fuente(FUENTE_TEXTO, 25),
}
fuente = recursos["texto"]

escena = "menu"     # "menu", "instrucciones" o "juego"
seleccion = 0       # opción marcada en el menú
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
                        menu.aplicar_volumen(sonidos.values(), volumen)
                        sonidos["hechizo"].play()
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
                    menu.aplicar_volumen(sonidos.values(), volumen)
                    sonidos["hechizo"].play()    # para escuchar cómo quedó
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
    bosque.dibujar_fondo(pantalla)
    bosque.dibujar_piedras(pantalla, False)
    bosque.dibujar_gato(pantalla)
    bosque.dibujar_piedras(pantalla, True)
    bosque.dibujar_frente(pantalla)

    if escena == "menu":
        menu.dibujar_menu(pantalla, recursos["titulo"], fuente, recursos["chica"], seleccion, volumen)
        dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())
    elif escena == "instrucciones":
        menu.dibujar_instrucciones(pantalla, recursos["subtitulo"], fuente, recursos["chica"])
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