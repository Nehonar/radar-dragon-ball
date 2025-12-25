# Decisiones Técnicas — Paso T10

## **Política de testing y validación (sin romper arquitectura)**

Este paso fija **cómo se valida que el sistema funciona** y, sobre todo,
**cómo se evita que los tests destruyan la arquitectura** (muy común con IA).

Seguimos **sin escribir código**.

---

## Problema a resolver

En sistemas con:

* concurrencia,
* UI,
* hardware,
* y simuladores,

es fácil que:

* los tests dependan del entorno,
* se “mockeen” cosas indebidas,
* se pruebe la UI en lugar del dominio,
* o se añadan hooks solo “para test”.

Eso **rompe contratos** y degrada el diseño.

---

## Principios obligatorios

1. **Se testea el dominio, no la UI**
2. **El simulador es la base del testing**
3. **No se añaden caminos solo para tests**
4. **Los tests no cambian arquitectura**
5. **Un test que viola contratos es inválido**

---

## Niveles de testing definidos

### 1 Tests de dominio (obligatorios)

**Qué se testea**

* `tracker`
* `mapping`
* `classifier`
* transiciones de estado de `Target`
* generación de `Snapshot`

**Cómo**

* usando `sim_scanner` o Observations sintéticas
* sin threads
* sin UI
* sin Runtime real

**Objetivo**

* validar lógica pura
* validar invariantes (θ fijo, r variable)
* validar degradación de datos erróneos

---

### 2 Tests de integración (limitados)

**Qué se testea**

* Scanner → Core
* Core → Snapshot
* manejo de colas llenas
* comportamiento ante ausencia de RF real

**Cómo**

* Runtime mínimo
* simulador activo
* sin UI gráfica

**Objetivo**

* validar contratos entre capas

---

### 3 Tests de UI (manuales / visuales)

**Qué se testea**

* render correcto
* estabilidad visual
* FPS
* inputs

**Cómo**

* ejecución manual
* simulador determinista
* escenarios predefinidos

**Nota**

> La UI **no se prueba automáticamente** en esta fase.

---

## Qué NO se testea (explícito)

Hardware real en CI
WiFi/BLE reales como dependencia
Rendimiento fino
Estética (más allá de estabilidad)

---

## Uso del simulador en testing

El simulador:

* es la fuente principal de tests
* genera escenarios reproducibles
* valida comportamiento extremo

Ejemplos de escenarios:

* 1 Target estable
* 10 Targets con RSSI similar
* Target que se acerca y se aleja
* Target que desaparece
* Ruido RF intenso

---

## Reglas obligatorias

* Los tests **no acceden a UI**
* Los tests **no acceden a Scanners reales**
* Los tests **no mutan estado interno**
* No se añaden flags tipo `TEST_MODE` en dominio
* No se “relajan” invariantes para que pase un test

---

## Encaje con Architecture Guard

* Refuerza separación de capas
* Evita mocks peligrosos
* Protege dominio
* IA no puede introducir test hacks

---

## Portabilidad futura

En ESP32:

* tests → simulación en host
* misma lógica de dominio
* mismo modelo mental

---

## Decisión T10 (formal)

**DT-010 — Testing basado en simulador y dominio puro**

* Dominio testeado con datos sintéticos
* UI validada manualmente
* Sin dependencia de hardware real
* Sin caminos especiales para test

**Estado:** Proposed
**Impacto:** Medio
**Reversible:** Sí
**Riesgo:** Bajo
