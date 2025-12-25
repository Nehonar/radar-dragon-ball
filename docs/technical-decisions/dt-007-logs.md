# Decisiones Técnicas — Paso T7

## **Logging, métricas y observabilidad mínima**

Este paso define **cómo se observa el sistema desde dentro** sin:

* contaminar la lógica,
* llenar el código de `print`,
* ni convertir el prototipo en algo frágil.

Es **clave** para depurar scanners, Core y concurrencia.

---

## Problema a resolver

El sistema es:

* concurrente,
* basado en eventos,
* con fuentes no deterministas (RF),
* y con UI desacoplada.

Si no definimos logging ahora:

* cada módulo loguea “a su manera”,
* aparecen prints temporales que se quedan,
* la IA añade logs en sitios incorrectos,
* y depurar problemas reales se vuelve difícil.

---

## Principios obligatorios

1. **Logging ≠ lógica**
2. **Logging no modifica comportamiento**
3. **Logs estructurados > prints**
4. **El Core no conoce destinos de logging**
5. **El logging no bloquea**

---

## Opciones evaluadas

### Opción A — `print()` en cada módulo

Rechazada

**Motivos**

* No estructurado
* Difícil de filtrar
* Contamina código
* IA abusa de él

---

### Opción B — `logging` estándar de Python

* Propuesta

**Motivos**

* Viene con Python
* Flexible
* Niveles claros
* Fácil de redirigir
* No introduce dependencias

---

### Opción C — Librerías externas (loguru, structlog)

Rechazadas por ahora

**Motivos**

* Añaden complejidad
* No necesarias en esta fase
* Dificultan portabilidad conceptual a ESP32

---

## Decisión

> **Usar el módulo `logging` estándar de Python como única vía de logging.**

---

## Niveles de logging (normativos)

### DEBUG

* Detalles internos
* Observations recibidas (resumidas)
* Cambios de estado de Targets
* Actividad del simulador

### INFO

* Arranque/parada de componentes
* Scanners habilitados
* Modo de ejecución
* Número de Targets activos

### WARNING

* Colas llenas
* Observations descartadas
* Scanners no disponibles
* Datos incompletos

### ERROR

* Fallos de scanner
* Excepciones no recuperables
* Inconsistencias graves

---

## Reglas obligatorias

1. **Nada de `print()`**

   * Todo logging pasa por `logging`

2. **Cada módulo tiene su logger**

   * Nombre basado en ruta del módulo
   * Ejemplo conceptual: `core.tracker`, `scanners.ble`

3. **El Core no formatea logs complejos**

   * No serializa grandes estructuras
   * No imprime Snapshots completos

4. **La UI loguea solo eventos**

   * No loguea cada frame
   * No loguea cada render

5. **Runtime configura logging**

   * Nivel global
   * Formato
   * Destino (stdout por defecto)

---

## Métricas mínimas (sin sistema de métricas formal)

Se permiten **contadores simples**, no más:

* Observations recibidas
* Observations descartadas
* Targets activos / stale
* Snapshots generados

Estas métricas:

* viven en Core
* se exponen solo vía logs o HUD (si procede)
* no disparan lógica

---

## Alternativas descartadas explícitamente

* Logs dentro de modelos (`Target`, `Observation`)
* Logging en tight loops de render
* Logging como mecanismo de control de flujo
* Uso de logging para “debug visual”

---

## Encaje con Architecture Guard

* Logging es infraestructura
* No altera dominio
* No introduce dependencias cruzadas
* IA sabe dónde puede y dónde no puede loguear

---

## Portabilidad futura

En ESP32:

* logging → UART / serial
* mismos niveles conceptuales
* misma intención semántica

---

## Decisión T7 (formal)

**DT-007 — Logging estructurado con `logging` estándar**

* Sin `print`
* Niveles claros
* Configurado por Runtime
* No bloqueante

**Estado:** Proposed
**Impacto:** Medio
**Reversible:** Sí
**Riesgo:** Bajo
