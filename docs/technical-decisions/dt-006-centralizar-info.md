# Decisiones Técnicas — Paso T6

## **Gestión de configuración y parámetros del sistema**

Esta decisión fija **cómo se configuran**:

* rangos de RSSI
* FPS
* tamaños de colas
* timeouts
* modos (simulador / real)
* flags de UI

Si esto no se define ahora:

* la config se dispersa,
* aparecen “numeritos mágicos”,
* la IA ajusta valores en sitios incorrectos,
* y el sistema se vuelve inconsistente.

---

## Problema a resolver

Necesitamos una forma de:

* centralizar parámetros,
* diferenciarlos de la lógica,
* permitir ajustes rápidos,
* sin romper contratos ni ADR.

Además:

* la config **no es dominio**
* pero **tampoco es UI**
* y **no debe vivir en Runtime “a ojo”**

---

## Principios obligatorios

1. **Una única fuente de verdad**
2. **Config es datos, no lógica**
3. **Valores explícitos, no implícitos**
4. **Cambiar config no cambia arquitectura**
5. **Config debe funcionar igual en simulador y real**

---

## Opciones evaluadas

### Opción A — Constantes repartidas por módulos

Rechazada

**Motivos**

* Inconsistencia
* Difícil de ajustar
* IA rompe cosas fácilmente

---

### Opción B — Archivo externo (YAML / JSON)

Válido más adelante, **no ahora**

**Motivos**

* Añade complejidad temprana
* No aporta aún beneficio claro
* Requiere parsing, validación, errores

---

### Opción C — Módulo `config` centralizado (Python)
Propuesta

---

## Decisión

> **Usar un módulo `core/config.py` como fuente central de configuración.**

Este módulo:

* define **solo valores**
* no contiene lógica
* es importado por:

  * Core
  * UI (solo lo necesario)
  * Runtime (solo flags)

---

## Categorías de configuración (obligatorias)

### 1 RF / Señal

* RSSI_MIN
* RSSI_MAX
* RSSI_SMOOTHING
* RSSI_STALE_TIMEOUT

---

### 2 Radar / Visual

* RADAR_RADIUS_MIN
* RADAR_RADIUS_MAX
* SWEEP_SPEED
* TARGET_SIZE_MIN/MAX
* JITTER_ENABLE (si existe)

---

### 3 Runtime / Performance

* UI_FPS
* CORE_TICK_RATE
* OBS_QUEUE_MAXSIZE
* SNAPSHOT_QUEUE_MAXSIZE (= 1)

---

### 4 Modos

* ENABLE_WIFI
* ENABLE_BLE
* ENABLE_SIMULATOR
* LOG_LEVEL

---

## Reglas obligatorias

* No se accede a config vía globals mutables
* No se modifica config en runtime
* Cambios de modo → reinicio limpio
* UI **no define** parámetros de dominio

---

## Alternativas descartadas explícitas

* Config “inline” en código
* Flags sueltos en Runtime
* Lectura directa de `os.environ` en dominio
* “Ajustes rápidos” en UI

Todas rompen disciplina y arquitectura.

---

## Encaje con Architecture Guard

* Refuerza separación dominio / infraestructura
* Evita números mágicos
* Hace explícitas decisiones implícitas
* IA sabe **dónde** tocar y **dónde no**

---

## Portabilidad futura

En ESP32:

* `config.h` o similar
* mismos parámetros
* mismo significado

Esto **reduce fricción de port**.

---

## Decisión T6 (formal)

**DT-006 — Configuración centralizada en módulo dedicado**

* Ubicación: `core/config.py`
* Sin lógica
* Valores explícitos
* Fuente única de verdad

**Estado:** Proposed
**Impacto:** Medio
**Reversible:** Sí
**Riesgo:** Bajo
