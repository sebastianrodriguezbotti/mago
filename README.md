# Bosque Encantado

Juego en Python y pygame que se controla con la cámara. Sos el guardián del bosque, un viejo oso que recuerda los sigilos antiguos: dibujá los sigilos en el aire con la mano para devolver a los espíritus a su sueño, y mové la cabeza para esquivar los golpes del Espíritu del Bosque.

Obligatorio 2 · Programación 2 · 2026

**Repositorio en GitHub:** https://github.com/sebastianrodriguezbotti/mago

---

## Instalación

Hace falta **Python 3.12** y una **cámara web**.

1. Descargá o cloná el repositorio y entrá a la carpeta del juego.
2. Instalá las librerías:

   ```
   pip install pygame opencv-python mediapipe==0.10.21
   ```

   Tiene que ser `mediapipe==0.10.21`: las versiones más nuevas no traen `mp.solutions`, que es lo que usa el juego para detectar la mano.

3. Ejecutá el juego:

   ```
   python main.py
   ```

En Windows, si tenés varios Python instalados, usá la ruta completa del que tiene las librerías, por ejemplo:

```
& "C:\Users\<usuario>\AppData\Local\Programs\Python\Python312\python.exe" main.py
```

---

## Cómo se juega

**Objetivo:** superar los 5 niveles sin que la barra de vida del guardián llegue a cero. Cada nivel que superás desbloquea el siguiente.

### Con la cámara
| Acción | Cómo |
|---|---|
| Dibujar un sigilo | Juntá el **índice y el pulgar** (pellizco) y mové la mano |
| Lanzar el hechizo | **Separá los dedos**: el trazo termina y se reconoce el sigilo |
| Esquivar al jefe | Mové la **cabeza** a los costados: el oso te sigue |

Los sigilos son cuatro: línea horizontal **—**, línea vertical **|**, **V** y **Λ**.

En la esquina de abajo a la derecha se ve la cámara chiquita, con un punto cian donde está tu varita.

### Con el teclado y el mouse
| Tecla | Qué hace |
|---|---|
| Flechas, Enter o mouse | Moverse y elegir en los menús |
| Esc | Pausa durante el juego · Salir desde el inicio |
| Enter | Saltear el cartel de un nivel o la historia |
| R | Jugar de nuevo cuando termina una partida |
| F11 | Pantalla completa / ventana |

### Los niveles
| Nivel | Qué pasa |
|---|---|
| 1 · El despertar | Espíritus con 1 sigilo |
| 2 · La niebla espesa | Espíritus con 2 sigilos: hay que dibujarlos en orden |
| 3 · Raíces que susurran | 2 sigilos, y a mitad del nivel el jefe sale de la tierra y ataca |
| 4 · Luna de huesos | 2 sigilos, y el jefe aparece dos veces |
| 5 · El corazón del bosque | Solo el jefe, con barra de vida: esquivá sus golpes y, cuando se descubra, dibujá su sigilo para dañarlo |

Cuando el jefe ataca, primero marca en el suelo dónde va a golpear (donde estás) y un momento después sale una garra: correte antes.

---

## Archivos

| Archivo | Qué tiene |
|---|---|
| `main.py` | Arma todo, maneja las pantallas y corre el bucle principal |
| `vision.py` | Todo lo de la cámara: abrir, leer el cuadro, detectar la mano (MediaPipe) y la cara (Haar) |
| `hechizos.py` | Reconoce qué sigilo se dibujó a partir de los puntos del trazo |
| `juego.py` | Las reglas de la partida y cómo se dibuja |
| `fantasma.py` | La clase `Fantasma` |
| `espiritu_piso.py` | La clase `EspirituDelPiso`: el jefe |
| `escenario.py` | El bosque: fondo, niebla, fuegos fatuos, luces y el oso |
| `menu.py` | Pantallas de inicio, niveles, pausa, cómo jugar y sonido |
| `historia.py` | La introducción que se cuenta antes del nivel 1 |
| `progreso.py` | Guarda en `progreso.json` cuántos niveles están desbloqueados |
| `ajustes.py` | Todas las constantes: colores, tamaños, velocidades, rangos de detección, niveles y textos |
| `img/` | Imágenes: fondos, oso, fantasma y jefe |
| `sonidos/` | Efectos de sonido (y `musica.ogg`, si está) |
| `fuentes/` | Tipografías Anton y Montserrat |

### Ajustes útiles (en `ajustes.py`)
- `PROPORCION_PELLIZCO`: si cuesta que dibuje, subilo a 0.45; si dibuja solo, bajalo a 0.25.
- `SENSIBILIDAD_CABEZA`: si cuesta llegar a los costados con la cabeza, subilo.
- `DESBLOQUEAR_TODO = True`: abre todos los niveles (para probar). Para empezar de cero, borrá `progreso.json`.
- `PANTALLA_COMPLETA = False`: arranca en ventana.
- `CAMARA_INDICE`: si no abre la cámara, probá con 1.

---

## Créditos
- Idea inspirada en *Magic Cat Academy*, el doodle de Google de Halloween 2016.
- Tipografías: Anton y Montserrat (Google Fonts, licencia SIL Open Font License).
- Ilustraciones: <COMPLETAR>.
- En el desarrollo se usó Claude (Anthropic), un asistente de IA. El detalle está en el informe.