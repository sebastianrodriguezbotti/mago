# probar_vision.py
# Prueba de vision.py y hechizos.py antes de armar el juego.
# - Juntá índice y pulgar y mové la mano: se dibuja el trazo.
# - Separá los dedos: el trazo termina y aparece qué símbolo reconoció.
# - C borra el trazo. La X cierra.

import pygame
import vision
from hechizos import reconocer_simbolo
from ajustes import ANCHO, ALTO, FPS, CUADROS_SIN_VARITA, COLOR_TRAZO, COLOR_TEXTO

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Prueba de la varita")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont(None, 36)

cap = vision.abrir_camara()
if cap is None:
    print("No se pudo abrir la cámara. Probá cambiar CAMARA_INDICE en ajustes.py")
    pygame.quit()
    raise SystemExit

trazo = []              # puntos del trazo que se está dibujando
sin_varita = 0          # cuántos cuadros seguidos no se vio la varita
ultimo_simbolo = "-"    # lo último que se reconoció

andando = True
while andando:
    # --- Eventos ---
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            andando = False
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_c:
            trazo = []

    # --- Actualizar ---
    frame = vision.leer_cuadro(cap)
    if frame is None:
        continue

    pos = vision.detectar_mano(frame)
    if pos is not None:
        trazo.append(pos)
        sin_varita = 0
    else:
        sin_varita += 1
        if sin_varita == CUADROS_SIN_VARITA and len(trazo) > 0:
            simbolo = reconocer_simbolo(trazo)
            if simbolo is None:
                ultimo_simbolo = "no reconocido"
            else:
                ultimo_simbolo = simbolo
            print("Trazo de", len(trazo), "puntos ->", ultimo_simbolo)
            trazo = []

    # --- Dibujar ---
    sup = pygame.image.frombuffer(frame.tobytes(), (ANCHO, ALTO), "BGR")
    pantalla.blit(sup, (0, 0))

    if len(trazo) >= 2:
        pygame.draw.lines(pantalla, COLOR_TRAZO, False, trazo, 6)
    if pos is not None:
        pygame.draw.circle(pantalla, COLOR_TRAZO, pos, 15, 3)

    texto = fuente.render("Símbolo: " + ultimo_simbolo, True, COLOR_TEXTO)
    pantalla.blit(texto, (10, 10))

    pygame.display.flip()
    reloj.tick(FPS)

cap.release()
pygame.quit()