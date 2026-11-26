# vision.py
# Todo lo de OpenCV y MediaPipe: abrir la cámara, leer el cuadro y detectar.
# El resto del juego solo usa lo que devuelven estas funciones: (x, y) o None.

import math
import cv2
import mediapipe as mp
from ajustes import (CAMARA_INDICE, ANCHO, ALTO, COLOR_MIN, COLOR_MAX,
                     AREA_MINIMA, PROPORCION_PELLIZCO,
                     ESPEJO_ANCHO, ESPEJO_ALTO, CARA_TAMANO_MINIMO)

# Lo que se prepara una sola vez, al hacer import vision
manos = mp.solutions.hands.Hands(max_num_hands=1)
caras = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if caras.empty():
    print("No se pudo cargar el detector de caras de OpenCV (haarcascade_frontalface_default.xml)")


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


def cuadro_espejo(frame):
    """Devuelve el cuadro chiquito, en gris teñido de azul, para el espejo de la esquina."""
    chico = cv2.resize(frame, (ESPEJO_ANCHO, ESPEJO_ALTO))
    gris = cv2.cvtColor(chico, cv2.COLOR_BGR2GRAY)
    azul = gris
    verde = (gris * 0.8).astype("uint8")
    rojo = (gris * 0.55).astype("uint8")
    return cv2.merge([azul, verde, rojo])    # en BGR: primero el azul


def a_pixeles(punto, ancho, alto):
    """Pasa un punto de MediaPipe (x e y entre 0 y 1) a píxeles."""
    return (int(punto.x * ancho), int(punto.y * alto))


# MediaPipe es lento: si en el mismo cuadro se pregunta por el dedo y por el pellizco,
# la mano se busca una sola vez y se guarda acá.
ultima_mano = {"frame": None, "puntos": None}


def puntos_de_la_mano(frame):
    """Busca la mano en el cuadro (una sola vez por cuadro).
    Devuelve un diccionario con los puntos que usa el juego, en píxeles, o None si no hay mano."""
    if ultima_mano["frame"] is frame:
        return ultima_mano["puntos"]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = manos.process(rgb)
    puntos = None
    if resultado.multi_hand_landmarks is not None:
        mano = resultado.multi_hand_landmarks[0]
        alto, ancho = frame.shape[:2]
        puntos = {
            "muneca": a_pixeles(mano.landmark[0], ancho, alto),
            "nudillo": a_pixeles(mano.landmark[9], ancho, alto),   # base del dedo medio
            "pulgar": a_pixeles(mano.landmark[4], ancho, alto),    # punta del pulgar
            "indice": a_pixeles(mano.landmark[8], ancho, alto),    # punta del índice
        }
    ultima_mano["frame"] = frame
    ultima_mano["puntos"] = puntos
    return puntos


def detectar_mano(frame):
    """Busca una mano haciendo 'pellizco' (índice y pulgar juntos).
    Devuelve (x, y), el punto entre las dos puntas, o None si no hay
    mano o si los dedos están separados."""
    p = puntos_de_la_mano(frame)
    if p is None:
        return None
    # El tamaño de la mano sirve de regla: así funciona cerca o lejos de la cámara
    tamano_mano = math.dist(p["muneca"], p["nudillo"])
    separacion = math.dist(p["pulgar"], p["indice"])
    if separacion > tamano_mano * PROPORCION_PELLIZCO:
        return None
    x = (p["pulgar"][0] + p["indice"][0]) // 2
    y = (p["pulgar"][1] + p["indice"][1]) // 2
    return (x, y)


def detectar_dedo(frame):
    """Para los menús: devuelve (x, y), la punta del índice, o None si no hay mano."""
    p = puntos_de_la_mano(frame)
    if p is None:
        return None
    return p["indice"]


def detectar_cara(frame):
    """Busca la cara más grande (con Haar, como en clase).
    Devuelve (x, y), el centro de la cara en la ventana, o None si no hay cara."""
    # se busca en una imagen 3 veces más chica: es mucho más rápido
    chico = cv2.resize(frame, (frame.shape[1] // 3, frame.shape[0] // 3))
    gris = cv2.cvtColor(chico, cv2.COLOR_BGR2GRAY)
    encontradas = caras.detectMultiScale(gris, scaleFactor=1.2, minNeighbors=5,
                                         minSize=(CARA_TAMANO_MINIMO, CARA_TAMANO_MINIMO))
    if len(encontradas) == 0:
        return None
    x, y, w, h = max(encontradas, key=lambda c: c[2] * c[3])   # la más grande: la más cercana
    return ((x + w // 2) * 3, (y + h // 2) * 3)


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