# Decisiones Técnicas — Paso T1

## Modelo de concurrencia y runtime en Python

Esta es **la decisión técnica más importante**, porque condiciona:

* cómo fluyen los datos
* cómo se sincroniza UI ↔ Core
* cómo se portará luego a ESP32
* qué errores aparecerán o no

---

## Problema a resolver

El sistema tiene **tres ritmos distintos**:

1. **Scanners**

   * I/O bloqueante
   * tiempos variables
   * eventos irregulares

2. **Core**

   * lógica determinista
   * bajo coste computacional
   * necesita coherencia

3. **UI**

   * loop gráfico
   * FPS constante
   * no debe bloquear nunca

Esto **no se puede resolver bien** con un único bucle lineal.

---

## Opciones técnicas reales

### Opción A — `asyncio` puro

**Descripción**

* Todo corre en un event loop
* Scanners asíncronos
* UI integrada o adaptada

**Pros**

* Un solo modelo mental
* Fácil cancelación
* Escala bien

**Contras**

* UI gráfica suele ser problemática
* BLE/WiFi suelen ser bloqueantes
* Mezclar `asyncio` + GUI es frágil
* Difícil de portar luego a ESP32 (modelo distinto)

---

### Opción B — Threads + Queues (modelo productor/consumidor)

**Descripción**

* Cada Scanner en su thread
* Core en su propio loop
* UI en el main thread
* Comunicación por `queue.Queue`

**Pros**

* Modelo simple y robusto
* Encaja con contratos (Observation → Snapshot)
* UI nunca bloquea
* Muy fácil de razonar
* Muy fácil de portar conceptualmente a ESP32 (tasks)
* Compatible con librerías bloqueantes

**Contras**

* Overhead de threads (aceptable)
* Hay que ser disciplinado con colas

---

### Opción C — Híbrido (threads + asyncio)

**Rechazada directamente**

**Motivo**

* Complejidad innecesaria
* Dos modelos mentales
* Alto riesgo de errores
* IA tiende a romperlo

---

## Decisión

> **Se adopta un modelo basado en threads + colas explícitas.**

### Concretamente:

* Cada Scanner corre en **su propio thread**
* El Core procesa Observations en **un loop dedicado**
* La UI corre en **el hilo principal**
* La comunicación se realiza **exclusivamente mediante colas**
* No hay estado compartido mutable entre threads

Esto **encaja perfectamente** con:

* ADR-004 (Snapshots)
* ADR-006 (Runtime pasivo)
* Architecture Guard

---

## Reglas técnicas derivadas

* No se usan locks explícitos entre Core y UI
* No se comparte memoria mutable
* Las colas tienen tamaño máximo
* La UI siempre renderiza el último Snapshot disponible
* El Core nunca espera a la UI

---

## Portabilidad (muy importante)

Este modelo se traduce 1:1 a ESP32:

| Python    | ESP32           |
| --------- | --------------- |
| Thread    | Task            |
| Queue     | Queue           |
| Runtime   | Main task       |
| Core loop | Processing task |

Esto **no es casual**, es una ventaja estratégica.

---

## Decisión T1 (formal)

**DT-001 — Modelo de concurrencia basado en threads y colas**

* Estado: Proposed
* Impacto: Alto
* Reversible: Sí (pero costoso)
* Riesgo: Bajo

