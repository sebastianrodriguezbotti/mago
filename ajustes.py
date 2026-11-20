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

# --- Partida ---
VIDAS = 3
PUNTOS_POR_FANTASMA = 10
CUADROS_CARTEL = 150       # cuánto dura el cartel que presenta cada nivel (5 segundos)

# --- Pantalla de niveles: una tarjeta por nivel ---
TARJETA_ANCHO = 150
TARJETA_ALTO = 190
TARJETA_SEPARACION = 22
TARJETAS_Y = 200           # borde de arriba de las tarjetas

# --- Progreso ---
ARCHIVO_PROGRESO = "progreso.json"   # acá se guarda cuántos niveles están desbloqueados
DESBLOQUEAR_TODO = False             # True para probar (o para la defensa): todos abiertos

# --- Niveles ---
# Cada nivel es un diccionario. Para cambiar la dificultad, se toca acá y nada más.
#   fantasmas: cuántos aparecen en total
#   velocidad: píxeles por cuadro
#   espera:    cuadros entre un fantasma y el siguiente
#   novedades: lo que se muestra en el cartel al empezar el nivel
NIVELES = [
    {
        "nombre": "El despertar",
        "fantasmas": 8,
        "velocidad": 1.2,
        "espera": 75,
        "novedades": ["Dibujá el sigilo de cada espíritu para espantarlo."],
    },
    {
        "nombre": "La niebla espesa",
        "fantasmas": 10,
        "velocidad": 1.6,
        "espera": 65,
        "novedades": ["Los espíritus se mueven más rápido."],
    },
    {
        "nombre": "Raíces que susurran",
        "fantasmas": 12,
        "velocidad": 2.0,
        "espera": 55,
        "novedades": ["Vienen más espíritus, y más seguido."],
    },
    {
        "nombre": "Luna de huesos",
        "fantasmas": 14,
        "velocidad": 2.3,
        "espera": 48,
        "novedades": ["La noche se pone más oscura."],
    },
    {
        "nombre": "El corazón del bosque",
        "fantasmas": 16,
        "velocidad": 2.6,
        "espera": 42,
        "novedades": ["Lo que duerme bajo el bosque está despertando."],
    },
]

# --- Sonido ---
VOLUMEN_EFECTOS_INICIAL = 0.7   # entre 0 y 1
VOLUMEN_MUSICA_INICIAL = 0.5
PASO_VOLUMEN = 0.1              # cuánto cambia con cada flecha
# Música de fondo: si existe un archivo con este nombre (.ogg, .mp3 o .wav), suena en loop.
MUSICA = "sonidos/musica"

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
TITULO_JUEGO = ["BOSQUE", "ENCANTADO"]   # una línea por elemento
FRASE_INICIO = ["Protegé al gato mago hasta que", "el bosque vuelva a dormir"]   # abajo a la derecha
IMAGEN_FONDO_MENU = "img/fondo_completo"   # sin extensión: prueba .png, .jpg y .jpeg
# Durante el juego el fondo son dos capas. Las dos se estiran al ancho de la ventana
# sin deformarse: el cielo se pega arriba y el piso abajo, encima del cielo.
IMAGEN_CIELO = "img/fondo2"
IMAGEN_PISO = "img/fondo1"                 # PNG con la parte de arriba transparente
MENU_X = 72                # todo el menú está alineado a la izquierda, a esta distancia del borde
TITULO_Y = 40              # borde de arriba del título
TITULO_TAMANO = 120
TITULO_INTERLINEADO = 112  # distancia entre las dos líneas del título
TITULO_ANCHO_MAXIMO = ANCHO - 2 * MENU_X   # si el título es más ancho, se achica
MENU_Y = 362               # altura de la primera opción
MENU_SEPARACION = 48       # distancia entre opciones
PAUSA_Y = 290              # altura de la primera opción de la pausa (tiene más opciones)
TAMANO_MENU = 26           # letra de las opciones
BARRA_X = MENU_X + 300     # dónde empiezan las barras de volumen
BARRA_ANCHO = 280

# --- Tipografías ---
# Bajalas de fonts.google.com (Anton y Montserrat) y guardalas en la carpeta fuentes/.
# Si no están, se usan parecidas que vienen con Windows.
FUENTE_TITULO = "Anton-Regular.ttf"          # títulos: condensada y gruesa
FUENTE_TEXTO = "Montserrat-Medium.ttf"       # todo lo demás
RESPALDO_TITULO = "impact,arialblack"
RESPALDO_TEXTO = "segoeui,arial"

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
BLANCO = (240, 250, 255)           # letras del título y del menú

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