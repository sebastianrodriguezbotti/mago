# menu.py
# Las pantallas de inicio, "Cómo jugar" y "Música y sonido".
# Acá están el dibujo de cada pantalla y qué hace cada tecla o clic en ellas.

import pygame
from escenario import mezclar
from fantasma import dibujar_simbolo
from ajustes import *

OPCIONES = ["Jugar", "Niveles", "Cómo jugar", "Música y sonido", "Salir"]
OPCIONES_SONIDO = ["Música", "Efectos", "Volver"]
OPCIONES_PAUSA = ["Continuar", "Niveles", "Cómo jugar", "Música y sonido",
                  "Volver al inicio", "Salir del juego"]


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


def borronear(sup, cuanto):
    """Devuelve la superficie borroneada: se achica y se vuelve a agrandar, y pierde detalle."""
    ancho, alto = sup.get_size()
    chica = pygame.transform.smoothscale(sup, (max(1, ancho // cuanto), max(1, alto // cuanto)))
    return pygame.transform.smoothscale(chica, (ancho, alto))


def crear_titulo(fuente):
    """Arma una sola vez el título del juego: letras blancas con resplandor cian.
    Si queda más ancho que TITULO_ANCHO_MAXIMO, lo achica.
    Devuelve (superficie, margen): el margen es el espacio que se dejó para el resplandor."""
    margen = 40
    renglones = [fuente.render(linea, True, BLANCO) for linea in TITULO_JUEGO]
    ancho = max(r.get_width() for r in renglones) + margen * 2
    alto = TITULO_INTERLINEADO * (len(renglones) - 1) + renglones[-1].get_height() + margen * 2

    letras = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    cian = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for i in range(len(TITULO_JUEGO)):
        y = margen + i * TITULO_INTERLINEADO
        letras.blit(renglones[i], (margen, y))
        cian.blit(fuente.render(TITULO_JUEGO[i], True, CIAN), (margen, y))

    # el resplandor: las letras en cian, borroneadas. Uno cercano y fuerte, otro amplio y suave.
    titulo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    cerca = borronear(cian, 6)
    lejos = borronear(cian, 16)
    titulo.blit(lejos, (0, 0))
    titulo.blit(cerca, (0, 0))
    titulo.blit(cerca, (0, 0))
    titulo.blit(letras, (0, 0))

    if ancho - margen * 2 > TITULO_ANCHO_MAXIMO:
        escala = TITULO_ANCHO_MAXIMO / (ancho - margen * 2)
        titulo = pygame.transform.smoothscale(titulo, (int(ancho * escala), int(alto * escala)))
        margen = int(margen * escala)
    return (titulo, margen)


def dibujar_titulo(pantalla, titulo):
    """titulo es lo que devolvió crear_titulo: (superficie, margen)."""
    sup, margen = titulo
    pantalla.blit(sup, (MENU_X - margen, TITULO_Y - margen))


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

def y_inicio(lista):
    """Devuelve la altura de la primera opción de la lista. La pausa empieza más arriba."""
    if lista is OPCIONES_PAUSA:
        return PAUSA_Y
    return MENU_Y


def rect_opcion(fuente, lista, i):
    """Devuelve el rectángulo que ocupa la opción i de la lista en la pantalla."""
    if lista is OPCIONES_SONIDO and lista[i] != "Volver":
        ancho = BARRA_X + BARRA_ANCHO - MENU_X     # la fila entera, con la barra
    else:
        ancho = fuente.size(lista[i].upper())[0]
    alto = fuente.get_height()
    return pygame.Rect(MENU_X - 30, y_inicio(lista) + i * MENU_SEPARACION - alto // 2, ancho + 60, alto)


def opcion_bajo_mouse(fuente, lista, pos):
    """Devuelve el número de la opción que está bajo el mouse, o None."""
    for i in range(len(lista)):
        if rect_opcion(fuente, lista, i).collidepoint(pos):
            return i
    return None


# ---------- Qué hace cada tecla o clic ----------

def evento_menu(e, fuente, seleccion, lista=OPCIONES, al_escape="Salir"):
    """Recibe un evento en una lista de opciones (la de inicio o la de pausa).
    Devuelve (seleccion, eleccion): eleccion es el texto de la opción elegida, o None.
    Esc elige la opción al_escape."""
    eleccion = None
    if e.type == pygame.MOUSEMOTION:
        debajo = opcion_bajo_mouse(fuente, lista, e.pos)
        if debajo is not None:
            seleccion = debajo
    elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        debajo = opcion_bajo_mouse(fuente, lista, e.pos)
        if debajo is not None:
            seleccion = debajo
            eleccion = lista[seleccion]
    elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            eleccion = al_escape
        elif e.key == pygame.K_UP:
            seleccion = (seleccion - 1) % len(lista)
        elif e.key == pygame.K_DOWN:
            seleccion = (seleccion + 1) % len(lista)
        elif e.key == pygame.K_RETURN:
            eleccion = lista[seleccion]
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


def evento_instrucciones(e, fuente):
    """Recibe un evento en "Cómo jugar". Devuelve "volver" si hay que volver al menú, o None."""
    if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
        return "volver"
    if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
        if rect_volver_instrucciones(fuente).collidepoint(e.pos):
            return "volver"
    return None


def rect_volver_instrucciones(fuente):
    """Devuelve el rectángulo del botón VOLVER de "Cómo jugar"."""
    ancho, alto = fuente.size("VOLVER")
    return pygame.Rect(MENU_X - 30, ALTO - 60 - alto // 2, ancho + 60, alto)


# ---------- Pantalla de niveles ----------
# La selección va de 0 a 4 (las tarjetas) y 5 es el botón VOLVER.

def rect_tarjeta(i):
    """Devuelve el rectángulo de la tarjeta del nivel i."""
    total = len(NIVELES) * TARJETA_ANCHO + (len(NIVELES) - 1) * TARJETA_SEPARACION
    x = (ANCHO - total) // 2 + i * (TARJETA_ANCHO + TARJETA_SEPARACION)
    return pygame.Rect(x, TARJETAS_Y, TARJETA_ANCHO, TARJETA_ALTO)


def evento_niveles(e, fuente, seleccion, desbloqueados):
    """Recibe un evento en la pantalla de niveles.
    Devuelve (seleccion, que_paso): que_paso es "jugar", "bloqueado", "volver" o None.
    Con "jugar", el nivel elegido es seleccion."""
    volver = len(NIVELES)          # el número que corresponde al botón VOLVER
    elegir = False
    que_paso = None
    if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
        debajo = None
        for i in range(len(NIVELES)):
            if rect_tarjeta(i).collidepoint(e.pos):
                debajo = i
        if rect_volver_instrucciones(fuente).collidepoint(e.pos):
            debajo = volver
        if debajo is not None:
            seleccion = debajo
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                elegir = True
    elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
            que_paso = "volver"
        elif e.key == pygame.K_LEFT and seleccion < volver:
            seleccion = (seleccion - 1) % len(NIVELES)
        elif e.key == pygame.K_RIGHT and seleccion < volver:
            seleccion = (seleccion + 1) % len(NIVELES)
        elif e.key == pygame.K_DOWN:
            seleccion = volver
        elif e.key == pygame.K_UP and seleccion == volver:
            seleccion = desbloqueados - 1
        elif e.key == pygame.K_RETURN:
            elegir = True

    if elegir:
        if seleccion == volver:
            que_paso = "volver"
        elif seleccion < desbloqueados:
            que_paso = "jugar"
        else:
            que_paso = "bloqueado"
    return seleccion, que_paso


def dibujar_candado(pantalla, cx, cy, color):
    """Un candado hecho con formas: el arco de arriba, el cuerpo y el ojo de la llave."""
    pygame.draw.circle(pantalla, color, (cx, cy - 10), 13, 4, draw_top_left=True, draw_top_right=True)
    pygame.draw.line(pantalla, color, (cx - 12, cy - 10), (cx - 12, cy - 2), 4)
    pygame.draw.line(pantalla, color, (cx + 11, cy - 10), (cx + 11, cy - 2), 4)
    pygame.draw.rect(pantalla, color, (cx - 19, cy - 2, 38, 30), border_radius=5)
    pygame.draw.circle(pantalla, NOCHE_1, (cx, cy + 10), 4)
    pygame.draw.line(pantalla, NOCHE_1, (cx, cy + 10), (cx, cy + 19), 3)


def dibujar_niveles(pantalla, fuente_titulo, fuente_numero, fuente, fuente_chica, seleccion, desbloqueados):
    escribir(pantalla, fuente_titulo, "NIVELES", BLANCO, (MENU_X, 110), "midleft")

    for i in range(len(NIVELES)):
        rect = rect_tarjeta(i)
        abierto = i < desbloqueados
        elegida = i == seleccion

        fondo = pygame.Surface(rect.size, pygame.SRCALPHA)
        fondo.fill((*NOCHE_1, 190))
        pantalla.blit(fondo, rect.topleft)
        if elegida:
            pygame.draw.rect(pantalla, CIAN, rect, 2)
            # el rombo celeste, arriba de la tarjeta elegida
            cx = rect.centerx
            pygame.draw.polygon(pantalla, CIAN, [(cx, rect.top - 22), (cx + 7, rect.top - 15),
                                                 (cx, rect.top - 8), (cx - 7, rect.top - 15)])
        else:
            pygame.draw.rect(pantalla, mezclar(NOCHE_1, PLATA, 0.6), rect, 1)

        if abierto:
            if elegida:
                escribir_brillante(pantalla, fuente_numero, str(i + 1), (rect.centerx, rect.top + 70))
            else:
                escribir(pantalla, fuente_numero, str(i + 1), BLANCO, (rect.centerx, rect.top + 70))
            # el nombre, en dos renglones si es largo
            palabras = NIVELES[i]["nombre"].upper().split()
            mitad = (len(palabras) + 1) // 2
            renglones = [" ".join(palabras[:mitad]), " ".join(palabras[mitad:])]
            for j in range(len(renglones)):
                escribir(pantalla, fuente_chica, renglones[j], BLANCO, (rect.centerx, rect.top + 135 + j * 22))
        else:
            gris = mezclar(NOCHE_1, PLATA, 0.45)
            escribir(pantalla, fuente_numero, str(i + 1), gris, (rect.centerx, rect.top + 70))
            dibujar_candado(pantalla, rect.centerx, rect.top + 135, PLATA if elegida else gris)

    # debajo de las tarjetas: qué pasa con la elegida
    if seleccion < len(NIVELES):
        if seleccion < desbloqueados:
            texto = "Enter o clic para jugar este nivel"
        else:
            texto = f"Superá el nivel {seleccion} para desbloquearlo"
        escribir(pantalla, fuente_chica, texto, PLATA, (ANCHO // 2, TARJETAS_Y + TARJETA_ALTO + 40))

    dibujar_opcion(pantalla, fuente, "Volver", ALTO - 60, seleccion == len(NIVELES))


# ---------- Pantallas ----------

def dibujar_opcion(pantalla, fuente, texto, y, elegida):
    """Una opción del menú, en mayúsculas y alineada a la izquierda.
    La elegida brilla, se corre un poco y tiene un rombo celeste al costado."""
    texto = texto.upper()
    if elegida:
        # una runa chiquita a la izquierda marca la opción elegida
        cx = MENU_X - 18
        pygame.draw.polygon(pantalla, CIAN, [(cx, y - 6), (cx + 6, y), (cx, y + 6), (cx - 6, y)])
        escribir_brillante(pantalla, fuente, texto, (MENU_X + 10, y), "midleft")
    else:
        escribir(pantalla, fuente, texto, BLANCO, (MENU_X, y), "midleft")


def dibujar_menu(pantalla, titulo, fuente, fuente_chica, seleccion):
    dibujar_titulo(pantalla, titulo)
    for i in range(len(OPCIONES)):
        dibujar_opcion(pantalla, fuente, OPCIONES[i], MENU_Y + i * MENU_SEPARACION, i == seleccion)
    # la frase de abajo a la derecha, cada renglón centrado en el mismo eje
    alto = fuente_chica.get_height()
    for i in range(len(FRASE_INICIO)):
        y = ALTO - 40 - (len(FRASE_INICIO) - 1 - i) * alto
        escribir(pantalla, fuente_chica, FRASE_INICIO[i], BLANCO, (ANCHO - 170, y))


def dibujar_pausa(pantalla, fuente_titulo, fuente, seleccion):
    escribir(pantalla, fuente_titulo, "PAUSA", BLANCO, (MENU_X, PAUSA_Y - 95), "midleft")
    for i in range(len(OPCIONES_PAUSA)):
        dibujar_opcion(pantalla, fuente, OPCIONES_PAUSA[i], PAUSA_Y + i * MENU_SEPARACION, i == seleccion)


def dibujar_barra(pantalla, y, volumen):
    """Barra de volumen: una línea de plata, la parte llena en cian y una perilla."""
    pygame.draw.line(pantalla, mezclar(NOCHE_1, PLATA, 0.6), (BARRA_X, y), (BARRA_X + BARRA_ANCHO, y), 2)
    lleno = int(BARRA_ANCHO * volumen)
    if lleno > 0:
        pygame.draw.line(pantalla, CIAN, (BARRA_X, y), (BARRA_X + lleno, y), 4)
    pygame.draw.circle(pantalla, CIAN_CLARO, (BARRA_X + lleno, y), 7)
    pygame.draw.circle(pantalla, NOCHE_1, (BARRA_X + lleno, y), 3)


def dibujar_sonido(pantalla, titulo, fuente, fuente_chica, seleccion, volumenes):
    dibujar_titulo(pantalla, titulo)
    for i in range(len(OPCIONES_SONIDO)):
        y = MENU_Y + i * MENU_SEPARACION
        opcion = OPCIONES_SONIDO[i]
        dibujar_opcion(pantalla, fuente, opcion, y, i == seleccion)
        if opcion != "Volver":
            clave = "musica" if opcion == "Música" else "efectos"
            dibujar_barra(pantalla, y, volumenes[clave])
            escribir(pantalla, fuente_chica, f"{int(volumenes[clave] * 100)}%", BLANCO_AZULADO,
                     (BARRA_X + BARRA_ANCHO + 25, y), "midleft")


def crear_sombra_izquierda():
    """Una sombra que oscurece la mitad izquierda de la pantalla, para leer bien el texto.
    Se crea una sola vez."""
    sombra = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    hasta = int(ANCHO * 0.8)
    for x in range(hasta):
        alfa = int(215 * (1 - x / hasta))
        pygame.draw.line(sombra, (*NOCHE_1, alfa), (x, 0), (x, ALTO))
    return sombra


def dibujar_instrucciones(pantalla, fuente_titulo, fuente, fuente_chica, sombra):
    pantalla.blit(sombra, (0, 0))
    escribir(pantalla, fuente_titulo, "CÓMO JUGAR", BLANCO, (MENU_X, 70), "midleft")

    y = 140
    escribir(pantalla, fuente, "OBJETIVO", CIAN, (MENU_X, y), "midleft")
    objetivo = [
        "Protegé al gato mago de los espíritus del bosque.",
        "Superá los cinco niveles para que el bosque vuelva a dormir.",
        "Cada nivel que superás desbloquea el siguiente.",
    ]
    for i in range(len(objetivo)):
        escribir(pantalla, fuente_chica, objetivo[i], BLANCO, (MENU_X, y + 34 + i * 26), "midleft")

    y = 250
    escribir(pantalla, fuente, "CÓMO SE JUEGA", CIAN, (MENU_X, y), "midleft")
    lineas = [
        "Cada espíritu lleva un sigilo sobre la cabeza.",
        "Juntá el índice y el pulgar y dibujá ese sigilo en el aire.",
        "Separá los dedos para lanzar el hechizo:",
        "se desvanecen todos los espíritus con ese sigilo.",
        "Si uno toca al gato, perdés una vida. Tenés tres.",
        "Desde el nivel 3 sale un gigante del piso: mové la cabeza para esquivarlo.",
    ]
    for i in range(len(lineas)):
        escribir(pantalla, fuente_chica, lineas[i], BLANCO, (MENU_X, y + 34 + i * 26), "midleft")

    # los cuatro sigilos que existen
    simbolos = ["—", "|", "V", "Λ"]
    for i in range(len(simbolos)):
        dibujar_simbolo(pantalla, simbolos[i], MENU_X + 20 + i * 90, 470, 18)

    # el único botón: VOLVER, siempre elegido
    dibujar_opcion(pantalla, fuente, "Volver", ALTO - 60, True)