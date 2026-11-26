# main.py
# Bosque Encantado: dibujá en el aire el sigilo de cada espíritu para espantarlo.
# Este archivo arma todo, maneja las escenas (menú, instrucciones, sonido, juego, pausa)
# y corre el bucle principal. Las reglas de la partida están en juego.py.

import pygame
import vision
import menu
import juego
import progreso
import espiritu_piso
import historia
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
# SCALED: el juego se dibuja en ANCHO x ALTO y pygame lo estira a la pantalla (y ajusta el mouse)
if PANTALLA_COMPLETA:
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED | pygame.FULLSCREEN)
else:
    pantalla = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
pygame.display.set_caption("Noche de Fantasmas")
pygame.mouse.set_visible(False)      # el cursor es un fuego fatuo
reloj = pygame.time.Clock()

sonidos = {
    "hechizo": pygame.mixer.Sound("sonidos/hechizo.wav"),
    "fallo": pygame.mixer.Sound("sonidos/fallo.wav"),
    "dano": pygame.mixer.Sound("sonidos/dano.wav"),
    "fin": pygame.mixer.Sound("sonidos/fin.wav"),
    "nivel": pygame.mixer.Sound("sonidos/nivel.wav"),
    "temblor": pygame.mixer.Sound("sonidos/temblor.wav"),
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

bosque = Bosque()                    # carga también la imagen del oso
espiritu_piso.cargar_imagenes()      # el gigante y su garra
# imágenes: si alguna no está, queda None y se usa el bosque dibujado
fondo_menu = cargar_imagen_fondo(IMAGEN_FONDO_MENU)
cielo = cargar_imagen_fondo(IMAGEN_CIELO, capa=True)    # atrás, pegado arriba
piso = cargar_imagen_fondo(IMAGEN_PISO, capa=True)      # encima del cielo, pegado abajo

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
    "numero": cargar_fuente(FUENTE_TITULO, 80),
}
recursos["titulo_juego"] = menu.crear_titulo(cargar_fuente(FUENTE_TITULO, TITULO_TAMANO))
fuente_menu = cargar_fuente(FUENTE_TEXTO, TAMANO_MENU)
sombra_izquierda = menu.crear_sombra_izquierda()
fuente = recursos["texto"]

escena = "menu"     # "menu", "historia", "niveles", "instrucciones", "sonido", "juego" o "pausa"
volver_a = "menu"   # a dónde vuelven "Niveles", "Cómo jugar" y "Música y sonido": al inicio o a la pausa
desbloqueados = progreso.cargar_progreso()   # cuántos niveles se pueden jugar
nivel_elegido = 0   # en qué nivel empieza la próxima partida
seleccion_niveles = 0   # tarjeta marcada en "Niveles" (la última es VOLVER)
pagina_historia = 0     # qué página de la historia se está mostrando
cuadros_historia = 0    # cuadros desde que empezó la página (para el texto letra por letra)
seleccion = 0       # opción marcada en el menú
seleccion_sonido = 0  # opción marcada en "Música y sonido"
seleccion_pausa = 0   # opción marcada en la pausa
destino = None      # a qué escena vamos cuando hay un fundido; None si no hay
fundido = 255       # 0 = se ve todo, 255 = todo negro. Arranca en negro y aparece.
partida = juego.nueva_partida()
pos = None
puntero = None          # en los menús: dónde está la punta del índice (None si no se ve la mano)
pellizco_antes = False  # si en el cuadro anterior había pellizco
sin_pellizco = 0        # cuadros seguidos sin pellizco (para que un pellizco largo no haga dos clics)


# ---------- Bucle principal ----------

andando = True
while andando:

    # --- Eventos ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            andando = False
        if e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
            pygame.display.toggle_fullscreen()      # pantalla completa <-> ventana

        if destino is not None:
            continue            # durante un fundido no se aceptan teclas

        if escena == "menu":
            seleccion, eleccion = menu.evento_menu(e, fuente_menu, seleccion)
            if eleccion == "Jugar":
                nivel_elegido = desbloqueados - 1     # sigue desde el último nivel desbloqueado
                destino = "juego"
                if nivel_elegido == 0:
                    destino = "historia"              # antes del nivel 1 se cuenta la historia
            elif eleccion == "Niveles":
                destino = "niveles"
                volver_a = "menu"
                seleccion_niveles = desbloqueados - 1
            elif eleccion == "Cómo jugar":
                destino = "instrucciones"
                volver_a = "menu"
            elif eleccion == "Música y sonido":
                destino = "sonido"
                volver_a = "menu"
                seleccion_sonido = 0
            elif eleccion == "Salir":
                destino = "salir"

        elif escena == "pausa":
            seleccion_pausa, eleccion = menu.evento_menu(e, fuente_menu, seleccion_pausa,
                                                         menu.OPCIONES_PAUSA, "Continuar")
            # dentro de la pausa se cambia de pantalla sin fundido: el juego queda congelado atrás
            if eleccion == "Continuar":
                escena = "juego"
                volver_a = "menu"
            elif eleccion == "Niveles":
                escena = "niveles"
                volver_a = "pausa"
                seleccion_niveles = partida["nivel"]
            elif eleccion == "Cómo jugar":
                escena = "instrucciones"
                volver_a = "pausa"
            elif eleccion == "Música y sonido":
                escena = "sonido"
                volver_a = "pausa"
                seleccion_sonido = 0
            elif eleccion == "Volver al inicio":
                destino = "menu"
            elif eleccion == "Salir del juego":
                destino = "salir"

        elif escena == "sonido":
            seleccion_sonido, que_paso = menu.evento_sonido(e, fuente_menu, seleccion_sonido, volumenes)
            if que_paso == "cambio":
                pygame.mixer.music.set_volume(volumenes["musica"])
                menu.aplicar_volumen(sonidos.values(), volumenes["efectos"])
                sonidos["hechizo"].play()    # para escuchar cómo quedó
            elif que_paso == "volver":
                if volver_a == "pausa":
                    escena = "pausa"
                else:
                    destino = "menu"

        elif escena == "niveles":
            seleccion_niveles, que_paso = menu.evento_niveles(e, fuente_menu, seleccion_niveles, desbloqueados)
            if que_paso == "jugar":
                nivel_elegido = seleccion_niveles
                destino = "juego"
                if nivel_elegido == 0:
                    destino = "historia"
            elif que_paso == "bloqueado":
                sonidos["fallo"].play()
            elif que_paso == "volver":
                if volver_a == "pausa":
                    escena = "pausa"
                else:
                    destino = "menu"

        elif escena == "historia":
            pagina_historia, cuadros_historia, termino = historia.evento_historia(
                e, pagina_historia, cuadros_historia)
            if termino:
                destino = "juego"

        elif escena == "instrucciones":
            if menu.evento_instrucciones(e, fuente_menu) == "volver":
                if volver_a == "pausa":
                    escena = "pausa"
                else:
                    destino = "menu"

        elif escena == "juego" and e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if partida["estado"] in ("perdiste", "ganaste"):
                    destino = "menu"          # la partida ya terminó: directo al inicio
                else:
                    escena = "pausa"
                    seleccion_pausa = 0
            elif e.key == pygame.K_RETURN:
                juego.saltar_cartel(partida)
            elif e.key == pygame.K_r and partida["estado"] in ("perdiste", "ganaste"):
                nivel_elegido = partida["inicio"]    # de nuevo desde el mismo nivel
                destino = "juego"

    # --- Fundido a negro entre escenas ---
    if destino is not None:
        fundido = min(255, fundido + VELOCIDAD_FUNDIDO)
        if fundido == 255:
            # ya está todo negro: recién ahora se cambia de escena
            if destino == "salir":
                andando = False
            elif destino == "juego":
                partida = juego.nueva_partida(nivel_elegido)
            elif destino == "historia":
                pagina_historia = 0
                cuadros_historia = 0
            if destino in ("menu", "juego"):
                volver_a = "menu"
            escena = destino
            destino = None
    elif fundido > 0:
        fundido = max(0, fundido - VELOCIDAD_FUNDIDO)

    # --- Cámara ---
    frame = vision.leer_cuadro(cap)
    pellizco = False
    if frame is not None and escena == "juego":
        if juego.usa_cabeza(partida):
            pos = vision.detectar_cara(frame)      # esquivando: se mueve con la cabeza
        else:
            pos = vision.detectar_mano(frame)      # dibujando: la mano
            pellizco = pos is not None
    else:
        pos = None

    # En los menús la mano es un mouse: el índice mueve el cursor y pellizcar hace clic.
    # Se "inventan" los mismos eventos que manda el mouse, así los menús no cambian.
    puntero = None
    if frame is not None and escena != "juego" and destino is None:
        puntero = vision.detectar_dedo(frame)
        pinza = vision.detectar_mano(frame)
        pellizco = pinza is not None
        if pinza is not None:
            puntero = pinza
        if puntero is not None:
            pygame.event.post(pygame.event.Event(pygame.MOUSEMOTION, pos=puntero, rel=(0, 0), buttons=(0, 0, 0)))

    pellizco_nuevo = pellizco and not pellizco_antes and sin_pellizco >= CUADROS_ENTRE_CLICS
    if pellizco:
        sin_pellizco = 0
    else:
        sin_pellizco += 1
    pellizco_antes = pellizco

    if pellizco_nuevo and destino is None:
        if escena != "juego" and puntero is not None:
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=puntero, button=1))
        elif escena == "juego" and partida["estado"] == "cartel":
            juego.saltar_cartel(partida)
        elif escena == "juego" and partida["estado"] in ("perdiste", "ganaste"):
            nivel_elegido = partida["inicio"]
            destino = "juego"

    # --- Actualizar ---
    bosque.actualizar()
    if escena == "historia":
        cuadros_historia += 1
    if escena == "juego":
        for nombre in juego.actualizar(partida, pos):
            sonidos[nombre].play()
        if partida["completado"] is not None:
            # se superó un nivel: se desbloquea el siguiente y se guarda en el archivo
            desbloqueados = progreso.desbloquear(desbloqueados, partida["completado"])
            partida["completado"] = None

    # --- Dibujar ---
    # de atrás hacia adelante: lo que se dibuja después queda encima.
    # La partida se ve en el juego, en la pausa y en las pantallas abiertas desde la pausa.
    en_partida = escena in ("juego", "pausa") or volver_a == "pausa"

    if en_partida:
        if cielo is not None and piso is not None:
            pantalla.blit(cielo, (0, 0))                        # el cielo, pegado arriba
            pantalla.blit(piso, (0, ALTO - piso.get_height()))  # el piso, pegado abajo
            juego.dibujar_gigante(pantalla, partida, recursos)  # el gigante, en el medio
            bosque.dibujar_fuegos(pantalla)
            bosque.dibujar_oso(pantalla, partida["oso_x"])
        else:
            bosque.dibujar_fondo(pantalla)
            bosque.dibujar_piedras(pantalla, False)
            juego.dibujar_gigante(pantalla, partida, recursos)
            bosque.dibujar_oso(pantalla, partida["oso_x"])
            bosque.dibujar_piedras(pantalla, True)
            bosque.dibujar_frente(pantalla)
        juego.dibujar_ataque(pantalla, partida, recursos)      # la marca y la garra, encima del oso
        juego.dibujar_fantasmas(pantalla, partida, recursos)   # los fantasmas, arriba de todo
        juego.dibujar_interfaz(pantalla, partida, pos, recursos, completa=(escena == "juego"))
        if escena == "juego" and frame is not None:
            dibujar_espejo(pantalla, frame, pos)
        if escena != "juego":
            pantalla.blit(velo, (0, 0))             # el juego congelado queda oscurecido atrás
    elif fondo_menu is not None:
        pantalla.blit(fondo_menu, (0, 0))
    else:
        bosque.dibujar_fondo(pantalla)
        bosque.dibujar_piedras(pantalla, False)
        bosque.dibujar_oso(pantalla)
        bosque.dibujar_piedras(pantalla, True)
        bosque.dibujar_frente(pantalla)

    if escena == "historia":
        historia.dibujar_historia(pantalla, recursos["texto"], recursos["chica"],
                                  pagina_historia, cuadros_historia, velo)
    elif escena == "menu":
        menu.dibujar_menu(pantalla, recursos["titulo_juego"], fuente_menu, recursos["chica"], seleccion)
    elif escena == "niveles":
        menu.dibujar_niveles(pantalla, recursos["titulo"], recursos["numero"], fuente_menu, recursos["chica"],
                             seleccion_niveles, desbloqueados)
    elif escena == "pausa":
        menu.dibujar_pausa(pantalla, recursos["titulo"], fuente_menu, seleccion_pausa)
    elif escena == "sonido":
        menu.dibujar_sonido(pantalla, recursos["titulo_juego"], fuente_menu, recursos["chica"],
                            seleccion_sonido, volumenes)
    elif escena == "instrucciones":
        menu.dibujar_instrucciones(pantalla, recursos["titulo"], fuente_menu, recursos["chica"], sombra_izquierda)
    if escena != "juego":
        if puntero is not None:
            dibujar_cursor(pantalla, bosque.brillo_chico, puntero)     # el cursor sigue a la mano
        else:
            dibujar_cursor(pantalla, bosque.brillo_chico, pygame.mouse.get_pos())

    if fundido > 0:
        negro.set_alpha(fundido)
        pantalla.blit(negro, (0, 0))

    pygame.display.flip()
    reloj.tick(FPS)

cap.release()
pygame.quit()