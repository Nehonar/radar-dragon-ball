# ADR-002 — RSSI tratado como **proximidad relativa**, no distancia física

**Estado:** Accepted
**Fecha:** *24/12/2025*
**Decisores:** *Nehonar / Radar Dragon ball*
**Alcance:** Core / Mapping / UI (transversal)

---

## Contexto

El sistema utiliza **RSSI (Received Signal Strength Indicator)** como principal señal cuantitativa para representar la cercanía de dispositivos WiFi/BLE.

En muchos proyectos similares se comete el error de:

* intentar convertir RSSI a metros,
* aplicar modelos de propagación,
* introducir calibraciones dependientes del entorno,
* o prometer “precisión” que el hardware no puede garantizar.

Esto genera:

* falsas expectativas,
* comportamiento errático,
* complejidad innecesaria,
* y decisiones de diseño equivocadas en UI y lógica.

---

## Decisión

Se establece explícitamente que:

> **RSSI representa proximidad relativa, no distancia física.**

Consecuencias directas de esta decisión:

* El sistema **no calcula metros**.
* El sistema **no calibra entorno**.
* El sistema **no compara RSSI entre dispositivos distintos como valores absolutos**.
* El sistema **solo usa RSSI para ordenar y normalizar cercanía visual**.

El mapeo RSSI → representación visual es:

* **determinista**
* **parametrizable**
* **clampado**
* **suavizado**
* **no reversible a metros**

---

## Alternativas consideradas

### Alternativa A — Convertir RSSI a metros

* Rechazada

**Motivos**

* RSSI depende de:

  * orientación de antena
  * potencia de emisión
  * obstáculos
  * cuerpo humano
* El resultado es inestable y engañoso.
* Introduce falsa “autoridad científica”.

---

### Alternativa B — Calibración por dispositivo

* Rechazada

**Motivos**

* Requiere perfiles por fabricante.
* No escala.
* Imposible con MAC randomizada.
* Rompe el modo simulador.

---

### Alternativa C — Clasificación por zonas discretas

* Considerada, pero **no exclusiva**

**Nota**

* Se permite internamente (NEAR / MID / FAR),
* pero siempre derivado de RSSI relativo,
* nunca como distancia real.

---

## Consecuencias

### Positivas

* Sistema honesto y estable.
* UI coherente con la realidad física.
* Portabilidad PC ↔ ESP32 sin recalibración.
* Simulador simple y fiable.
* IA no puede “mejorar” inventando métricas falsas.

### Negativas

* No se puede responder “¿a cuántos metros?”
* Algunos usuarios pueden pedir más precisión.

Estas consecuencias son **aceptadas conscientemente**.

---

## Relación con contratos

Este ADR:

* **refuerza** `/docs/contracts/invariants.md` (Invariante 3)
* **prohíbe** añadir cualquier campo tipo `distance_m`
* **obliga** a que `radius_norm` sea abstracto

Cualquier intento de:

* inferir metros,
* exponer distancia real,
* o calibrar RSSI

**viola este ADR**.

---

## Regla derivada (normativa)

> Si una funcionalidad requiere distancia real,
> **no pertenece a este sistema**.

---

## Cierre ADR-002

Este ADR define la **honestidad física** del sistema.
Todos los componentes deben asumir RSSI como **señal cualitativa**, no métrica absoluta.

