# ADR-003 — Representación **2D** de Targets mediante dirección fija y radio variable

**Estado:** Accepted
**Fecha:** *24/12/2025*
**Decisores:** *Nehonar / Radar Dragon ball*
**Alcance:** Core / Mapping / UI

---

## Contexto

El sistema visualiza dispositivos detectados (Targets) mediante un **radar bidimensional (2D)**, inspirado en representaciones clásicas como el radar de *Dragon Ball*.

El sistema **no dispone de información espacial real** (dirección o posición física), únicamente de **intensidad de señal (RSSI)**. Por tanto, cualquier representación espacial debe ser **honesta**, **estable** y **no engañosa**.

Es necesario evitar:

* saltos visuales,
* movimientos erráticos,
* interpretaciones de profundidad o dirección real,
* y ambigüedades sobre dimensiones espaciales.

---

## Decisión

Se establece que:

> **Todos los Targets se representan en un plano 2D cartesiano, derivados de un sistema polar (θ, r).**

Cada Target tiene:

* una **dirección fija** (ángulo θ),
* una **distancia variable al centro** (radio r),
* y una **posición 2D coherente** durante toda su vida.

---

## Reglas obligatorias de representación

1. **Radar estrictamente 2D**

   * No existe eje Z.
   * No existe profundidad ni volumen.
   * No se emplean capas, perspectiva ni pseudo-3D.

2. **Asignación de dirección (θ)**

   * A cada Target se le asigna un **ángulo θ** al crearse.
   * El ángulo θ se deriva de forma **determinista o pseudoaleatoria estable** (por ejemplo, a partir del `id`).
   * El ángulo θ **no cambia** durante la vida del Target.

3. **Cálculo de distancia (r)**

   * El radio r se calcula **exclusivamente** a partir del RSSI filtrado.
   * RSSI más alto → r menor (más cerca del centro).
   * RSSI más bajo → r mayor (más lejos del centro).
   * No se muestra ni se infiere distancia física real.

4. **Conversión a coordenadas 2D**

   * La posición final del Target se obtiene mediante:

     ```
     x = r · cos(θ)
     y = r · sin(θ)
     ```
   * Targets con RSSI similar comparten radio, pero **nunca posición exacta** (θ distinto).

5. **Movimiento permitido**

   * Un Target **solo puede moverse radialmente**.
   * Los cambios de RSSI producen desplazamiento **en línea recta hacia o desde el centro**.
   * No se permite movimiento angular.

6. **Estabilidad visual**

   * No se recalcula θ en lecturas sucesivas.
   * No se reordena visualmente por intensidad.
   * No se permite “orbitar”, “derivar” o saltar lateralmente.

---

## Alternativas consideradas

### Alternativa A — Radar 3D o pseudo-3D

* Rechazada
Motivo:

* Sugiere información espacial inexistente.
* Introduce complejidad visual falsa.
* Rompe la estética y legibilidad tipo *Dragon Ball*.

---

### Alternativa B — Posición completamente aleatoria por frame

* Rechazada
Motivo:

* Produce ruido visual.
* Impide seguimiento humano.
* Introduce falsos movimientos.

---

### Alternativa C — Ángulo basado en orden de detección

* Rechazada
Motivo:

* No determinista.
* Inestable ante latencia o pérdida de paquetes.
* Difícil de reproducir y depurar.

---

## Consecuencias

### Positivas

* Radar claro e inmediatamente comprensible.
* Movimiento visual coherente y legible.
* Correspondencia directa RSSI → cercanía visual.
* Representación honesta sin falsas promesas espaciales.

### Negativas

* El ángulo no tiene significado físico.
* No se representa dirección real.

Estas consecuencias son **aceptadas explícitamente**.

---

## Relación con contratos

Este ADR:

* Refuerza los contratos de `Target.angle` y `Target.radius`.
* Garantiza la **Invariante de estabilidad visual**.
* Prohíbe cualquier representación que sugiera:

  * profundidad,
  * dirección física,
  * o movimiento angular real.

Cualquier implementación que:

* cambie θ durante la vida del Target,
* mueva Targets lateralmente,
* o represente capas espaciales,

**viola este ADR**.

---

## Regla derivada (normativa)

> Un Target **no cambia de dirección**,
> solo se acerca o se aleja del origen.

---

## Cierre

Este ADR define de forma inequívoca la **representación espacial 2D** del radar y es vinculante para cualquier implementación presente o futura.
