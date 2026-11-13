# ajustes.py
# Todas las constantes del juego en un solo lugar.

# --- Ventana y cámara ---
CAMARA_INDICE = 0          # 0 es la cámara de la compu. Si no anda, probá 1.
ANCHO = 640
ALTO = 480
FPS = 30

# --- Detección por color (en HSV) ---
# Rango para un objeto VERDE (tapita, marcador, pelotita).
# Para calibrar: corré probar_vision.py, hacé clic sobre tu objeto
# y mirá en la terminal qué valores H, S, V tiene.
COLOR_MIN = (40, 80, 80)
COLOR_MAX = (85, 255, 255)
AREA_MINIMA = 500          # manchas más chicas que esto se consideran ruido

# --- Trazo ---
CUADROS_SIN_VARITA = 5     # cuadros seguidos sin detectar para dar el trazo por terminado
PUNTOS_MINIMOS = 10        # un trazo con menos puntos no cuenta como símbolo
PROPORCION_LINEA = 2       # ancho > alto * 2  -> línea horizontal (y al revés)
CUADROS_AVISO = 90         # 3 segundos sin varita -> aviso en pantalla

# --- Gato ---
GATO_X = ANCHO // 2
GATO_Y = ALTO - 70
RADIO_GATO = 40

# --- Fantasmas ---
SIMBOLOS = ["—", "|", "V", "Λ"]
RADIO_FANTASMA = 25
VELOCIDAD_FANTASMA = 1.0       # píxeles por cuadro en la oleada 1
AUMENTO_VELOCIDAD = 0.4        # cuánto más rápido en cada oleada
FANTASMAS_POR_OLEADA = 6
CUADROS_ENTRE_FANTASMAS = 75   # 2,5 segundos a 30 FPS

# --- Partida ---
VIDAS = 3
OLEADAS_PARA_GANAR = 3
PUNTOS_POR_FANTASMA = 10

# --- Colores (RGB, para pygame) ---
COLOR_TRAZO = (182, 255, 63)
COLOR_TEXTO = (255, 255, 255)
COLOR_FANTASMA = (235, 235, 255)
COLOR_OJOS = (30, 30, 50)
COLOR_SIMBOLO = (255, 220, 60)
COLOR_GATO = (60, 60, 70)
COLOR_SOMBRERO = (110, 60, 200)
COLOR_AVISO = (255, 90, 90)