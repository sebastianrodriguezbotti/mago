# Bosque Encantado

Juego en Python y pygame que se controla con la cámara. Sos el guardián del bosque, un viejo oso que recuerda los sigilos antiguos: dibujá los sigilos en el aire con la mano para devolver a los espíritus a su sueño, y mové la cabeza para esquivar los golpes del Espíritu del Bosque.

Obligatorio 2 · Programación 2 · 2026

**Repositorio en GitHub:** <PEGAR ACÁ EL LINK DEL REPOSITORIO>

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

## Para que la cámara detecte bien
- **Luz:** una habitación bien iluminada, con la luz de frente o de costado. A contraluz (una ventana detrás tuyo) la mano y la cara se detectan peor.
- **Fondo:** un fondo liso y sin otras personas. Si hay más de una cara, el juego sigue a la más grande (la más cercana).
- **Distancia:** entre 50 cm y 1,5 m de la cámara, con la mano entera dentro del cuadro. El pellizco se mide en proporción al tamaño de la mano, así que funciona cerca y lejos.
- **La mano:** de frente a la cámara, con la palma hacia adelante. Para dibujar, juntá bien las puntas del índice y el pulgar; para soltar, separalas claramente.
- **La cara:** de frente, sin taparla con la mano. Para esquivar alcanza con mover la cabeza (no hace falta mover el cuerpo).
- Si no detecta nada, el juego no se rompe: el oso se queda quieto y aparece un aviso.

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
| `probar_vision.py` | Programa aparte para probar la detección de la mano y el reconocimiento de sigilos (no es parte del juego) |
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

## Bibliotecas
- **pygame:** ventana, dibujo, sonido y eventos.
- **opencv-python:** cámara, imagen y detección de caras (clasificador Haar).
- **mediapipe 0.10.21:** detección de los puntos de la mano.

Además se usan módulos que vienen con Python: `math`, `random`, `os` y `json`.

---

## Origen y licencia de los recursos
| Recurso | Origen | Licencia |
|---|---|---|
| Ilustraciones (`img/`) | <COMPLETAR: propias / herramienta usada> | <COMPLETAR> |
| Efectos de sonido (`sonidos/*.wav`) | Generados por código (síntesis de ondas y ruido), para este juego | Propios |
| Música (`sonidos/musica.ogg`) | Generada por código (acordes, zumbido, viento y campanas), para este juego | Propia |
| Tipografías Anton y Montserrat | Google Fonts | SIL Open Font License 1.1 |
| Idea de dibujar símbolos para espantar fantasmas | Inspirada en *Magic Cat Academy* (Google, 2016) | Solo referencia, no se usa material del original |

---

## Uso de Inteligencia Artificial Generativa
Usé **Claude** (Anthropic) como asistente durante el desarrollo:

- **Código:** generación y corrección del código en Python a partir de mis indicaciones de diseño, por etapas (un commit por cambio). Revisé, probé con mi cámara y comenté el código.
- **Ideas:** propuestas de mecánicas a partir de mis pedidos (niveles, jefe, esquivar con la cabeza).
- **Errores:** interpretar mensajes de error e instalar bibliotecas.
- **Sonidos:** los efectos y la música se generaron con código escrito con ayuda de la IA.
- **Documentación:** redacción inicial del README y del informe, que revisé y completé.

Las decisiones de diseño son mías: la estética, el boceto del menú, la historia del oso, los niveles y las ilustraciones.

**Prompts más relevantes** (resumidos):
1. "Desarrollar un juego en Python con pygame, inspirado en Magic Cat Academy de Google, controlado mediante la cámara web."
2. "Reemplazar la detección por color por la detección de la mano con MediaPipe, utilizando la mano como varita."
3. "Incorporar un menú de inicio con instrucciones, salida con la tecla Esc y control de volumen."
4. "Aplicar la estética Bosque Espectral definida: paleta, iluminación, elementos visuales, tipografía y movimiento."
5. "Estructurar el juego en cinco niveles: nivel 1 con espíritus de un sigilo, nivel 2 con dos sigilos, niveles 3 y 4 con apariciones del jefe y nivel 5 con el jefe como único enemigo."
6. "Implementar un enemigo que surge del suelo y ataca, que el jugador esquiva desplazándose horizontalmente con movimientos de la cabeza."
7. "Permitir la selección de las opciones de los menús mediante el gesto de pellizco."
8. "Redactar el README y el informe a partir del desarrollo realizado."

**Referencia (APA):**
Claude. (2026). *Prompts utilizados para la programación, la generación de sonidos y la redacción de la documentación del juego Bosque Encantado* [Generación de código y texto]. Recuperado de https://claude.ai

---

## Créditos
- Idea inspirada en *Magic Cat Academy*, el doodle de Google de Halloween 2016.
- Tipografías: Anton y Montserrat (Google Fonts, licencia SIL Open Font License).
- Ilustraciones: Generadas con midjouny, editadas en photoshop.