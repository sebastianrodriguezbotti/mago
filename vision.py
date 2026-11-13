# vision.py
# Todo lo de OpenCV y MediaPipe: abrir la cámara, leer el cuadro y detectar.
# El resto del juego solo usa lo que devuelven estas funciones: (x, y) o None.

import math
import cv2
import mediapipe as mp
from ajustes import (CAMARA_INDICE, ANCHO, ALTO, COLOR_MIN, COLOR_MAX,
                     AREA_MINIMA, PROPORCION_PELLIZCO)

# Lo que se prepara una sola vez, al hacer import vision
manos = mp.solutions.hands.Hands(max_num_hands=1)


def abrir_camara():
    """Abre la cámara y devuelve el objeto cap, o None si no se pudo."""
    cap = cv2.VideoCapture(CAMARA_INDICE)
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, ANCHO)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, ALTO)
    return cap


def leer_cuadro(cap):
    """Lee un cuadro, lo espeja y lo deja del tamaño de la ventana.
    Devuelve el cuadro en BGR, o None si la lectura falló."""
    ok, frame = cap.read()
    if not ok:
        return None
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (ANCHO, ALTO))
    return frame


def a_pixeles(punto, ancho, alto):
    """Pasa un punto de MediaPipe (x e y entre 0 y 1) a píxeles."""
    return (int(punto.x * ancho), int(punto.y * alto))


def detectar_mano(frame):
    """Busca una mano haciendo 'pellizco' (índice y pulgar juntos).
    Devuelve (x, y), el punto entre las dos puntas, o None si no hay
    mano o si los dedos están separados."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = manos.process(rgb)
    if resultado.multi_hand_landmarks is None:
        return None

    mano = resultado.multi_hand_landmarks[0]
    alto, ancho = frame.shape[:2]
    muneca = a_pixeles(mano.landmark[0], ancho, alto)
    nudillo = a_pixeles(mano.landmark[9], ancho, alto)   # base del dedo medio
    pulgar = a_pixeles(mano.landmark[4], ancho, alto)    # punta del pulgar
    indice = a_pixeles(mano.landmark[8], ancho, alto)    # punta del índice

    # El tamaño de la mano sirve de regla: así funciona cerca o lejos de la cámara
    tamano_mano = math.dist(muneca, nudillo)
    separacion = math.dist(pulgar, indice)
    if separacion > tamano_mano * PROPORCION_PELLIZCO:
        return None

    x = (pulgar[0] + indice[0]) // 2
    y = (pulgar[1] + indice[1]) // 2
    return (x, y)


def detectar_color(frame):
    """Versión anterior, con un objeto de color. Queda como alternativa.
    Devuelve (x, y), el centro de la mancha más grande, o None."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mascara = cv2.inRange(hsv, COLOR_MIN, COLOR_MAX)
    contornos, _ = cv2.findContours(
        mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contornos) == 0:
        return None
    grande = max(contornos, key=cv2.contourArea)
    if cv2.contourArea(grande) < AREA_MINIMA:
        return None
    x, y, w, h = cv2.boundingRect(grande)
    return (x + w // 2, y + h // 2)