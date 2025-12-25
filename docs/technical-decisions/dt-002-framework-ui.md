# Decisiones Técnicas — Paso T2

## Framework de UI en Python (Radar 2D + HUD)

Aquí decidimos **la tecnología de UI**. Esto fija:

* cómo renderizas el radar
* cómo gestionas input
* cómo empaquetas el prototipo
* qué tan fácil será iterar estética “retro”

---

## Requisitos técnicos (derivados de arquitectura)

La UI debe:

* correr en **main thread**
* renderizar 2D (puntos, líneas, texto, sweep)
* mantener FPS estable (p. ej. 30)
* consumir `Snapshot` inmutable
* ser fácil de distribuir en Ubuntu

---

## Opciones reales

### Opción A — Pygame

**Pros**

* 2D inmediato y simple
* Control total del look retro
* FPS, input y render muy directos
* Ideal para radar “tipo videojuego” (que es exactamente lo que quieres)
* Muy buena iteración rápida

**Contras**

* No es “UI de escritorio” tradicional (aunque sirve)
* Integración con widgets tradicionales limitada (no necesitas muchos)

---

### Opción B — PySide6 / PyQt (Qt)

**Pros**

* UI de escritorio nativa
* Widgets, menús, diálogos
* QPainter sirve para 2D

**Contras**

* Más boilerplate
* Iterar look “radar retro” suele ser más lento
* Riesgo de mezclar lógica UI con render complejo

---

### Opción C — Tkinter

**Pros**

* Viene con Python
* Simple

**Contras**

* Render 2D y FPS/animación menos cómodos
* Estética retro más limitada sin pelearte

---

## Decisión propuesta

> **Usar Pygame para el prototipo Python.**

Motivos:

* El radar es esencialmente una “escena 2D” en loop.
* Te da control fino del estilo (tipografía bitmap, parpadeos, scanlines).
* Menos fricción para iterar UI y efectos.
* Encaja perfecto con snapshots y colas.

---

## Reglas técnicas derivadas

* UI loop = main thread (Pygame event loop)
* Render dibuja solo desde el último `Snapshot`
* Input emite comandos a Runtime (no toca Core)
* No se accede a Scanners desde UI

---

## Decisión T2 (formal)

**DT-002 — UI en Python usando Pygame**

* Estado: Proposed
* Impacto: Medio-Alto
* Reversible: Sí
* Riesgo: Bajo

