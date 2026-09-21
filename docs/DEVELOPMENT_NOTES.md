# Notas de desarrollo

Este documento recoge problemas técnicos relevantes encontrados durante el
desarrollo de Typing Survivor y las decisiones tomadas para resolverlos.

## Pantalla completa inestable en Windows

### Problema

Al pulsar `F11`, la aplicación parpadeaba, alteraba temporalmente toda la
pantalla y minimizaba otras ventanas abiertas.

### Causa

La primera implementación recreaba la ventana con `pygame.FULLSCREEN`. Este
modo solicita pantalla completa exclusiva y puede hacer que Windows cambie el
modo de vídeo del monitor. Ese cambio era el responsable del parpadeo y del
comportamiento de las demás ventanas.

### Solución

Se sustituyó la pantalla completa exclusiva por una ventana sin bordes creada
con `pygame.NOFRAME` y las dimensiones actuales del escritorio. Esta solución
evita solicitar a Windows un cambio del modo de vídeo del monitor. Al ampliar,
la ventana se coloca en el origen del escritorio y, al salir, recupera su tamaño
y posición anteriores.

La aplicación conserva su superficie lógica de `1280 × 720` y continúa
escalando el fotograma de forma proporcional a la resolución disponible.

### Verificación

- Entrada y salida repetida del modo de pantalla completa con `F11`.
- Conservación del estado actual del juego al cambiar de modo.
- Regreso correcto al modo ventana.
- Interfaz escalada sin deformaciones.
- Ausencia de errores cuando el sistema rechaza un cambio de modo.

### Aprendizaje

Pantalla completa exclusiva y pantalla completa de escritorio no son
equivalentes. Para un juego 2D de escritorio que ya dispone de escalado
responsive, mantener la resolución del sistema ofrece una transición más
estable y una mejor convivencia con otras aplicaciones.
