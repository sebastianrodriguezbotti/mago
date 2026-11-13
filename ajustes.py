# ajustes.py
# Todas las constantes del juego en un solo lugar.

# --- Ventana y cámara ---
CAMARA_INDICE = 0          # 0 es la cámara de la compu. Si no anda, probá 1.
ANCHO = 960
ALTO = 640
FPS = 30

# --- Detección de la mano ---
# Se dibuja juntando índice y pulgar ("pellizco").
# Cuenta como pellizco si la distancia entre las dos puntas es menor que
# esta proporción del tamaño de la mano (muñeca -> base del dedo medio).
# Si cuesta que dibuje, subilo (0.45). Si dibuja solo, bajalo (0.25).
PROPORCION_PELLIZCO = 0.35

# --- Detección por color (alternativa, en HSV) ---
COLOR_MIN = (40, 80, 80)
COLOR_MAX = (85, 255, 255)
AREA_MINIMA = 500

# --- Espejo: la cámara chiquita en una esquina ---
ESPEJO_ANCHO = 192
ESPEJO_ALTO = 128
ESPEJO_MARGEN = 16

# --- Trazo ---
CUADROS_SIN_VARITA = 5     # cuadros seguidos sin pellizco para dar el trazo por terminado
PUNTOS_MINIMOS = 10        # un trazo con menos puntos no cuenta como símbolo
PROPORCION_LINEA = 2       # ancho > alto * 2  -> línea horizontal (y al revés)
CUADROS_AVISO = 120        # 4 segundos sin dibujar -> aviso en pantalla

# --- Gato y círculo de piedras ---
GATO_X = ANCHO // 2
GATO_Y = ALTO - 120
RADIO_GATO = 45
CIRCULO_RADIO_X = 170      # el círculo de piedras es una elipse alrededor del gato
CIRCULO_RADIO_Y = 40
CANTIDAD_PIEDRAS = 9
ALTO_PIEDRA = 50

# --- Fantasmas ---
SIMBOLOS = ["—", "|", "V", "Λ"]
RADIO_FANTASMA = 28
VELOCIDAD_FANTASMA = 1.2       # píxeles por cuadro en la oleada 1
AUMENTO_VELOCIDAD = 0.5        # cuánto más rápido en cada oleada
FANTASMAS_POR_OLEADA = 6
CUADROS_ENTRE_FANTASMAS = 75   # 2,5 segundos a 30 FPS

# --- Partida ---
VIDAS = 3
OLEADAS_PARA_GANAR = 3
PUNTOS_POR_FANTASMA = 10

# --- Sonido ---
VOLUMEN_INICIAL = 0.7      # entre 0 y 1
PASO_VOLUMEN = 0.1         # cuánto cambia con cada flecha

# --- Bosque (lo que se mueve en el fondo) ---
CANTIDAD_FUEGOS = 12           # fuegos fatuos flotando
VELOCIDAD_FUEGOS = 0.7
VELOCIDAD_NIEBLA = 0.4         # píxeles por cuadro
PROBABILIDAD_RAFAGA = 0.005    # en cada cuadro: 0.005 = una ráfaga cada ~7 segundos
FUERZA_RAFAGA = 22             # cuánto se doblan las ramas
VELOCIDAD_RESPIRAR = 0.05      # qué tan rápido suben y bajan de brillo los sigilos
PROBABILIDAD_OJOS = 0.003      # ojos que aparecen entre los árboles
VELOCIDAD_FUNDIDO = 15         # transición a negro: cuánto oscurece por cuadro (de 0 a 255)

# --- Menú ---
MENU_Y = 225               # altura de la primera opción
MENU_SEPARACION = 52       # distancia entre opciones

# --- Tipografías ---
# Bajalas de fonts.google.com y guardalas en la carpeta fuentes/.
# Si no están, se usa una fuente con serifa de Windows.
FUENTE_TITULO = "CinzelDecorative-Regular.ttf"
FUENTE_TEXTO = "CormorantGaramond-Medium.ttf"
FUENTE_RESPALDO = "palatinolinotype,bookantiqua,georgia,timesnewroman"

# --- Paleta "Bosque Espectral" (RGB) ---
# Regla: el cian es lo único que brilla.
NOCHE_1 = (5, 7, 15)           # #05070F
NOCHE_2 = (11, 20, 38)         # #0B1426
NOCHE_3 = (19, 35, 58)         # #13233A
GRIS_AZUL = (42, 59, 76)       # #2A3B4C  troncos, rocas, niebla
MUSGO = (47, 61, 53)           # #2F3D35
CIAN = (34, 211, 238)          # #22D3EE  la magia
CIAN_CLARO = (103, 232, 249)   # #67E8F9
PLATA = (156, 163, 175)        # #9CA3AF  marcos y bordes
BLANCO_AZULADO = (203, 213, 225)   # #CBD5E1  textos

# Nombres que usa el resto del código
COLOR_TRAZO = CIAN_CLARO
COLOR_TEXTO = BLANCO_AZULADO
COLOR_FANTASMA = (170, 190, 215)
COLOR_OJOS = NOCHE_1
COLOR_SIMBOLO = CIAN_CLARO
COLOR_GATO = NOCHE_1
COLOR_SOMBRERO = NOCHE_3
COLOR_AVISO = CIAN_CLARO
COLOR_ELEGIDO = CIAN
COLOR_APAGADO = PLATA