# vision.py
# Todo lo de OpenCV: abrir la cámara, leer el cuadro y detectar.
# El resto del juego solo usa lo que devuelven estas funciones.

import cv2
from ajustes import CAMARA_INDICE, ANCHO, ALTO, COLOR_MIN, COLOR_MAX, AREA_MINIMA


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


def detectar_varita(frame):
    """Busca el objeto del color de la varita.
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


def color_hsv(frame, x, y):
    """Devuelve el color (h, s, v) de un píxel. Sirve para calibrar."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[y, x]
    return (int(h), int(s), int(v))