# Decisiones Técnicas — Paso T8

## **Gestión de errores y tolerancia a fallos**

Este paso define **cómo falla el sistema**.
No cómo “evitar” errores (eso es imposible), sino **cómo se comporta cuando ocurren**, sin romper arquitectura ni experiencia.

---

## Problema a resolver

El sistema:

* depende de hardware externo (WiFi / BLE),
* usa threads,
* consume datos no deterministas,
* y renderiza continuamente.

Los fallos **van a ocurrir**:

* BLE no disponible
* WiFi bloqueado
* permisos insuficientes
* scanners que mueren
* datos corruptos
* colas llenas

Si no se define ahora:

* se lanzan excepciones sin control,
* el sistema se cae entero,
* la UI se congela,
* o la IA añade `try/except` arbitrarios.

---

## Principios obligatorios

1. **Fallar de forma aislada**
2. **Nunca bloquear la UI**
3. **Nunca corromper el Core**
4. **Preferir degradación a parada**
5. **Errores ≠ excepciones no capturadas**

---

## Clasificación de fallos (normativa)

### 1 Fallos de Scanner (esperados)

Ejemplos:

* BLE apagado
* WiFi no escanea
* comando externo falla
* dispositivo desaparece

**No son errores fatales**

---

### 2 Fallos de datos (esperados)

Ejemplos:

* RSSI fuera de rango
* Observation incompleta
* timestamp inválido

**Se descartan y se registran**

---

### 3️⃣ Fallos de infraestructura (críticos)

Ejemplos:

* cola no inicializada
* Core no arranca
* UI no se inicia

**Requieren parada controlada**

---

## Decisión

> **El sistema es tolerante a fallos de entrada, pero estricto con fallos estructurales.**

---

## Reglas obligatorias por componente

### Scanner

* Captura **todas** las excepciones internas
* Nunca propaga excepciones al Runtime
* En fallo:

  * registra error
  * se desactiva
  * permite que el sistema continúe

Nunca mata el proceso

---

### Core

* Valida Observations al consumirlas
* Descarta datos inválidos
* No lanza excepciones por datos erróneos
* Mantiene consistencia interna siempre

Nunca se bloquea esperando datos válidos

---

### UI

* Asume que puede no haber datos
* Renderiza estado vacío o último Snapshot
* Nunca depende de llegada continua de Snapshots

Nunca lanza excepción por falta de datos

---

### Runtime

* Supervisa el estado de componentes
* Decide parada limpia solo en fallos estructurales
* Nunca intenta “arreglar” lógica

---

## Estrategias explícitas

### Degradación elegante

* Si BLE falla → WiFi + simulador
* Si WiFi falla → BLE + simulador
* Si ambos fallan → solo simulador
* Si todo falla → UI sigue viva mostrando “NO DATA”

---

### Parada controlada

Solo se permite cuando:

* Core no puede arrancar
* UI no puede iniciarse
* Invariantes arquitectónicas se rompen

En ese caso:

* log ERROR
* cierre limpio de threads
* salida explícita

---

## Alternativas descartadas

“Fail fast” global
Reinicios automáticos silenciosos
Try/except masivos sin criterio
UI que decide errores de dominio

Todas violan separación de responsabilidades.

---

## Encaje con Architecture Guard

* Refuerza Runtime pasivo
* Evita lógica de dominio en manejo de errores
* Asegura estabilidad visual
* IA no puede añadir control de errores en capas incorrectas

---

## Portabilidad futura

En ESP32:

* fallos de sensores → degradación
* watchdog solo para fallos estructurales
* misma filosofía

---

## Decisión T8 (formal)

**DT-008 — Tolerancia a fallos con degradación elegante**

* Scanners fallan de forma aislada
* Core es robusto a datos erróneos
* UI nunca bloquea
* Runtime solo gestiona fallos críticos

**Estado:** Proposed
**Impacto:** Alto
**Reversible:** Difícil
**Riesgo:** Bajo
