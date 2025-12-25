# Decisiones Técnicas — Paso T4

## Formato interno de **eventos y colas** (Observation / Snapshot flow)

Esta decisión fija **cómo viajan los datos dentro del sistema**.
Si esto queda bien definido ahora, **no habrá refactors dolorosos después**.

---

## Problema a resolver

Con DT-001 aprobado (threads + colas), necesitamos decidir:

* cuántas colas existen
* quién escribe y quién lee
* si los mensajes son:

  * push
  * pull
  * broadcast
* cómo evitar:

  * bloqueos
  * pérdida silenciosa de datos
  * acoplamiento accidental

---

## Requisitos derivados de arquitectura

De ADR y Architecture Guard:

* Scanner **solo emite** `Observation`
* Core **consume Observations** y **produce Snapshots**
* UI **consume Snapshots**
* Runtime **no interpreta datos**
* No hay estado compartido mutable
* No hay dependencias inversas

---

## Opciones evaluadas

### Opción A — Una única cola global

Rechazada

**Motivos**

* Mezcla dominios distintos
* Dificulta razonamiento
* Riesgo de leer “lo que no toca”
* Muy fácil romper arquitectura

---

### Opción B — Cola por Scanner + cola UI

* Posible, pero innecesaria

**Motivos**

* Aumenta complejidad
* No aporta beneficio real
* Core tendría que multiplexar manualmente

---

### Opción C — Pipeline claro con **dos colas**

✔️ Propuesta

---

## Decisión

> **Usar exactamente dos colas explícitas y tipadas conceptualmente.**

### Cola 1 — `observation_queue`

* Productores: Scanners (WiFi, BLE, Sim)
* Consumidor: Core
* Contenido: `Observation`
* Dirección: Scanner → Core

### Cola 2 — `snapshot_queue`

* Productor: Core
* Consumidor: UI
* Contenido: `Snapshot`
* Dirección: Core → UI

No existen más colas de dominio.

---

## Reglas obligatorias

### observation_queue

* Tamaño máximo configurable
* Si está llena:

  * se permite descartar Observations
  * el descarte debe ser explícito (log/contador)
* El Core **consume continuamente**
* El Core **no bloquea esperando datos**

---

### snapshot_queue

* Tamaño máximo = 1 (o muy pequeño)
* Contiene **solo el último Snapshot**
* La UI:

  * consume cuando puede
  * siempre renderiza el Snapshot más reciente
* Snapshots antiguos pueden descartarse sin problema

---

## Por qué snapshot_queue = 1 es correcto

* La UI no necesita historial
* El render siempre quiere “lo último”
* Evita acumulación
* Evita latencia visual
* Refuerza el modelo “fotografías, no stream”

---

## Alternativas descartadas explícitamente

* Colas bidireccionales
* UI leyendo Observations
* Core leyendo input directamente
* Broadcast de estado mutable

Todas violan contratos y/o ADR.

---

## Encaje con Runtime (ADR-006)

El Runtime:

* crea las colas
* las pasa a cada componente
* no mira su contenido
* no transforma mensajes

---

## Portabilidad a ESP32

El modelo es 1:1:

| Python            | ESP32                  |
| ----------------- | ---------------------- |
| observation_queue | FreeRTOS Queue         |
| snapshot_queue    | FreeRTOS Queue (len 1) |
| thread            | task                   |

Esto **no es accidental**, es intencional.

---

## Decisión T4 (formal)

**DT-004 — Pipeline de datos con dos colas explícitas**

* observation_queue: Scanner → Core
* snapshot_queue: Core → UI
* Tamaños controlados
* Descartes explícitos

**Estado:** Proposed
**Impacto:** Alto
**Reversible:** Sí (pero costoso)
**Riesgo:** Bajo
