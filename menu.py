# menu.py
# Las pantallas de inicio, "Cómo jugar" y "Música y sonido".
# Acá están el dibujo de cada pantalla y qué hace cada tecla o clic en ellas.

import pygame
from escenario import mezclar
from fantasma import dibujar_simbolo
from ajustes import *

OPCIONES = ["Jugar", "Cómo jugar", "Música y sonido", "Salir"]
OPCIONES_SONIDO = ["Música", "Efectos", "Volver"]


# ---------- Texto ----------

def escribir(pantalla, fuente, texto, color, punto, ancla="center"):
    """Escribe un texto. ancla dice qué parte del texto va en punto:
    "center" (centrado) o "midleft" (alineado a la izquierda)."""
    sup = fuente.render(texto, True, color)
    rect = sup.get_rect(**{ancla: punto})
    pantalla.blit(sup, rect)


def escribir_brillante(pantalla, fuente, texto, punto, ancla="center"):
    """Texto cian con un halo suave alrededor."""
    # el halo: el mismo texto en cian oscuro, sobre negro, sumado (BLEND_ADD) varias veces corrido
    halo = fuente.render(texto, True, mezclar(NOCHE_1, CIAN, 0.18), (0, 0, 0))
    rect = halo.get_rect(**{ancla: punto})
    for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
        pantalla.blit(halo, rect.move(dx, dy), special_flags=pygame.BLEND_ADD)
    escribir(pantalla, fuente, texto, CIAN, punto, ancla)


def escribir_tallado(pantalla, fuente, texto, punto, ancla="center"):
    """Texto como tallado en piedra: una sombra oscura corrida y el texto claro arriba."""
    escribir(pantalla, fuente, texto, NOCHE_1, (punto[0] + 3, punto[1] + 3), ancla)
    escribir(pantalla, fuente, texto, BLANCO_AZULADO, punto, ancla)


def separador(pantalla, centro_y, ancho):
    """Una línea fina de plata con una runa (rombo) en el medio."""
    color = mezclar(NOCHE_1, PLATA, 0.55)
    cx = ANCHO // 2
    pygame.draw.line(pantalla, color, (cx - ancho // 2, centro_y), (cx - 12, centro_y), 1)
    pygame.draw.line(pantalla, color, (cx + 12, centro_y), (cx + ancho // 2, centro_y), 1)
    pygame.draw.polygon(pantalla, color, [(cx, centro_y - 6), (cx + 6, centro_y),
                                          (cx, centro_y + 6), (cx - 6, centro_y)], 1)
    pygame.draw.circle(pantalla, color, (cx - ancho // 2, centro_y), 2)
    pygame.draw.circle(pantalla, color, (cx + ancho // 2, centro_y), 2)


def crear_titulo(fuente):
    """Arma una sola vez el título del juego, con un brillo celeste suave alrededor.
    Si queda más ancho que TITULO_ANCHO_MAXIMO, lo achica. Devuelve la superficie."""
    texto = fuente.render(TITULO_JUEGO, True, BLANCO_AZULADO)
    halo = fuente.render(TITULO_JUEGO, True, CIAN)
    halo.set_alpha(22)                # muy transparente: brilla solo un poco
    margen = 12
    titulo = pygame.Surface((texto.get_width() + margen * 2, texto.get_height() + margen * 2),
                            pygame.SRCALPHA)
    # el halo se pega muchas veces alrededor, corrido: se acumula y parece un resplandor
    for dx in range(-6, 7, 2):
        for dy in range(-6, 7, 2):
            if dx * dx + dy * dy <= 36:
                titulo.blit(halo, (margen + dx, margen + dy))
    titulo.blit(texto, (margen, margen))

    if titulo.get_width() > TITULO_ANCHO_MAXIMO:
        escala = TITULO_ANCHO_MAXIMO / titulo.get_width()
        nuevo = (int(titulo.get_width() * escala), int(titulo.get_height() * escala))
        titulo = pygame.transform.smoothscale(titulo, nuevo)
    return titulo


# ---------- Volumen ----------

def cambiar_volumen(volumen, cambio):
    """Devuelve el volumen nuevo, siempre entre 0 y 1."""
    nuevo = round(volumen + cambio * PASO_VOLUMEN, 1)
    if nuevo < 0:
        nuevo = 0
    if nuevo > 1:
        nuevo = 1
    return nuevo


def aplicar_volumen(sonidos, volumen):
    """Le pone el mismo volumen a todos los sonidos de la lista."""
    for s in sonidos:
        s.set_volume(volumen)


def volumen_desde_mouse(x):
    """Devuelve el volumen según dónde se hizo clic en la barra (0 a la izquierda, 1 a la derecha)."""
    k = (x - BARRA_X) / BARRA_ANCHO
    k = max(0, min(1, k))
    return round(k, 1)


# ---------- Posición de las opciones (todas alineadas a la izquierda) ----------

def rect_opcion(fuente, lista, i):
    """Devuelve el rectángulo que ocupa la opción i de la lista en la pantalla."""
    if lista is OPCIONES_SONIDO and lista[i] != "Volver":
        ancho = BARRA_X + BARRA_ANCHO - MENU_X     # la fila entera, con la barra
    else:
        ancho = fuente.size(lista[i])[0]
    alto = fuente.get_height()
    return pygame.Rect(MENU_X - 30, MENU_Y + i * MENU_SEPARACION - alto // 2, ancho + 60, alto)


def opcion_bajo_mouse(fuente, lista, pos):
    """Devuelve el número de la opción que está bajo el mouse, o None."""
    for i in range(len(lista)):
        if rect_opcion(fuente, lista, i).collidepoint(pos):
            return i
    return None


# ---------- Qué hace cada tecla o clic ----------

def evento_menu(e, fuente, seleccion):
    """Recibe un evento en la pantalla de inicio.
    Devuelve (seleccion, eleccion): eleccion es el texto de la opción elegida, o None."""
    eleccion = None
    if e.type == pygame.MOUSEMOTION:
        debajo = opcion_bajo_mouse(fuente, OPCIONES, e.pos)
        if debajo is not None:
            seleccion = debajo
    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        debajo = opcion_bajo_mouse(fuente, OPCIONES, e.pos)
        if debajo is not None:
            seleccion = debajo
            eleccion = OPCIONES[seleccion]
    elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            eleccion = "Salir"
        elif e.key == pygame.K_UP:
            seleccion = (seleccion - 1) % len(OPCIONES)
        elif e.key == pygame.K_DOWN:
            seleccion = (seleccion + 1) % len(OPCIONES)
        elif e.key == pygame.K_RETURN:
            eleccion = OPCIONES[seleccion]
    return seleccion, eleccion


def evento_sonido(e, fuente, seleccion, volumenes):
    """Recibe un evento en la pantalla "Música y sonido". Cambia volumenes["musica"]
    o volumenes["efectos"]. Devuelve (seleccion, que_paso):
    que_paso es "volver", "cambio" (si cambió un volumen) o None."""
    que_paso = None
    if e.type == pygame.MOUSEMOTION:
        debajo = opcion_bajo_mouse(fuente, OPCIONES_SONIDO, e.pos)
        if debajo is not None:
            seleccion = debajo
    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        debajo = opcion_bajo_mouse(fuente, OPCIONES_SONIDO, e.pos)
        if debajo is not None:
            seleccion = debajo
            opcion = OPCIONES_SONIDO[seleccion]
            if opcion == "Volver":
                que_paso = "volver"
            elif e.pos[0] >= BARRA_X - 10:
                # clic sobre la barra: el volumen queda donde se hizo clic
                clave = "musica" if opcion == "Música" else "efectos"
                volumenes[clave] = volumen_desde_mouse(e.pos[0])
                que_paso = "cambio"
    elif e.type == pygame.KEYDOWN:
        opcion = OPCIONES_SONIDO[seleccion]
        if e.key == pygame.K_ESCAPE:
            que_paso = "volver"
        elif e.key == pygame.K_UP:
            seleccion = (seleccion - 1) % len(OPCIONES_SONIDO)
        elif e.key == pygame.K_DOWN:
            seleccion = (seleccion + 1) % len(OPCIONES_SONIDO)
        elif e.key == pygame.K_RETURN and opcion == "Volver":
            que_paso = "volver"
        elif e.key in (pygame.K_LEFT, pygame.K_RIGHT) and opcion != "Volver":
            cambio = -1 if e.key == pygame.K_LEFT else 1
            clave = "musica" if opcion == "Música" else "efectos"
            volumenes[clave] = cambiar_volumen(volumenes[clave], cambio)
            que_paso = "cambio"
    return seleccion, que_paso


# ---------- Pantallas ----------

def dibujar_opcion(pantalla, fuente, texto, y, elegida):
    """Una opción del menú, alineada a la izquierda. La elegida brilla y se corre un poco."""
    if elegida:
        # una runa chiquita a la izquierda marca la opción elegida
        cx = MENU_X - 18
        pygame.draw.polygon(pantalla, CIAN, [(cx, y - 6), (cx + 6, y), (cx, y + 6), (cx - 6, y)])
        escribir_brillante(pantalla, fuente, texto, (MENU_X + 10, y), "midleft")
    else:
        escribir(pantalla, fuente, texto, BLANCO_AZULADO, (MENU_X, y), "midleft")


def dibujar_menu(pantalla, titulo, fuente, fuente_chica, seleccion):
    pantalla.blit(titulo, (MENU_X - 12, TITULO_Y))
    for i in range(len(OPCIONES)):
        dibujar_opcion(pantalla, fuente, OPCIONES[i], MENU_Y + i * MENU_SEPARACION, i == seleccion)
    escribir(pantalla, fuente_chica, "Flechas o mouse para elegir  ·  Esc para salir",
             mezclar(NOCHE_1, PLATA, 0.8), (MENU_X, ALTO - 30), "midleft")


def dibujar_barra(pantalla, y, volumen):
    """Barra de volumen: una línea de plata, la parte llena en cian y una perilla."""
    pygame.draw.line(pantalla, mezclar(NOCHE_1, PLATA, 0.6), (BARRA_X, y), (BARRA_X + BARRA_ANCHO, y), 2)
    lleno = int(BARRA_ANCHO * volumen)
    if lleno > 0:
        pygame.draw.line(pantalla, CIAN, (BARRA_X, y), (BARRA_X + lleno, y), 4)
    pygame.draw.circle(pantalla, CIAN_CLARO, (BARRA_X + lleno, y), 7)
    pygame.draw.circle(pantalla, NOCHE_1, (BARRA_X + lleno, y), 3)


def dibujar_sonido(pantalla, titulo, fuente, fuente_chica, seleccion, volumenes):
    pantalla.blit(titulo, (MENU_X - 12, TITULO_Y))
    for i in range(len(OPCIONES_SONIDO)):
        y = MENU_Y + i * MENU_SEPARACION
        opcion = OPCIONES_SONIDO[i]
        dibujar_opcion(pantalla, fuente, opcion, y, i == seleccion)
        if opcion != "Volver":
            clave = "musica" if opcion == "Música" else "efectos"
            dibujar_barra(pantalla, y, volumenes[clave])
            escribir(pantalla, fuente_chica, f"{int(volumenes[clave] * 100)}%", BLANCO_AZULADO,
                     (BARRA_X + BARRA_ANCHO + 25, y), "midleft")
    escribir(pantalla, fuente_chica, "Flechas izquierda y derecha, o clic en la barra  ·  Esc para volver",
             mezclar(NOCHE_1, PLATA, 0.8), (MENU_X, ALTO - 30), "midleft")


def dibujar_instrucciones(pantalla, fuente_titulo, fuente, fuente_chica):
    # un panel oscuro con marco fino de plata
    panel = pygame.Rect(0, 0, 720, 570)
    panel.center = (ANCHO // 2, ALTO // 2)
    velo = pygame.Surface(panel.size, pygame.SRCALPHA)
    velo.fill((*NOCHE_1, 220))
    pantalla.blit(velo, panel.topleft)
    pygame.draw.rect(pantalla, PLATA, panel, 1)
    pygame.draw.rect(pantalla, mezclar(NOCHE_1, PLATA, 0.4), panel.inflate(-10, -10), 1)

    escribir_tallado(pantalla, fuente_titulo, "Cómo jugar", (ANCHO // 2, panel.top + 45))
    separador(pantalla, panel.top + 82, 300)

    y = panel.top + 110
    escribir(pantalla, fuente, "Objetivo", CIAN, (ANCHO // 2, y))
    objetivo = [
        "Protegé al gato mago de los espíritus del bosque.",
        "Superá los tres niveles para que el bosque vuelva a dormir.",
    ]
    for i in range(len(objetivo)):
        escribir(pantalla, fuente_chica, objetivo[i], BLANCO_AZULADO, (ANCHO // 2, y + 36 + i * 28))

    y = panel.top + 220
    escribir(pantalla, fuente, "Cómo se juega", CIAN, (ANCHO // 2, y))
    lineas = [
        "Cada espíritu lleva un sigilo sobre la cabeza.",
        "Juntá el índice y el pulgar y dibujá ese sigilo en el aire.",
        "Separá los dedos para lanzar el hechizo:",
        "se desvanecen todos los espíritus con ese sigilo.",
        "Si uno toca al gato, perdés una vida. Tenés tres.",
    ]
    for i in range(len(lineas)):
        escribir(pantalla, fuente_chica, lineas[i], BLANCO_AZULADO, (ANCHO // 2, y + 36 + i * 28))

    # los cuatro sigilos que existen
    simbolos = ["—", "|", "V", "Λ"]
    for i in range(len(simbolos)):
        x = ANCHO // 2 - 165 + i * 110
        dibujar_simbolo(pantalla, simbolos[i], x, panel.bottom - 85, 18)

    escribir(pantalla, fuente_chica, "Esc o Enter para volver", PLATA, (ANCHO // 2, panel.bottom - 30))