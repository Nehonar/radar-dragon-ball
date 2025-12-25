# Decisiones Técnicas — Paso T9

## **Ciclo de vida del sistema y apagado limpio (startup / shutdown)**

Este paso fija **cómo nace y cómo muere el sistema**.
Si esto queda claro ahora, evitas:

* hilos zombis,
* recursos sin liberar,
* estados corruptos,
* y “funciona hasta que no”.

---

## Problema a resolver

El sistema tiene:

* múltiples threads,
* colas compartidas,
* UI con loop propio,
* scanners que pueden fallar o bloquear.

Sin una política clara:

* cerrar la ventana no detiene threads,
* Ctrl+C deja recursos abiertos,
* el Core queda a medio estado,
* la IA mete `daemon=True` y “ya está”.

Eso **no es aceptable**.

---

## Principios obligatorios

1. **Un único punto de arranque**
2. **Un único punto de parada**
3. **La UI controla la vida visible**
4. **El Runtime controla la vida real**
5. **Nadie se apaga solo**

---

## Decisión

> **El Runtime es el único responsable del ciclo de vida completo del sistema.**

Esto incluye:

* startup ordenado,
* ejecución,
* shutdown limpio y explícito.

---

## Startup (orden obligatorio)

1. **Runtime inicia logging**
2. **Runtime carga configuración**
3. **Runtime crea colas**
4. **Runtime crea Core**
5. **Runtime crea Scanners**
6. **Runtime crea UI**
7. **Runtime lanza threads**
8. **Runtime entra en estado RUNNING**

Si algún paso falla:

* se registra ERROR
* se ejecuta shutdown limpio
* el sistema no queda a medio iniciar

---

## Ejecución (RUNNING)

Durante ejecución:

* Scanners producen Observations
* Core consume y produce Snapshots
* UI renderiza y recibe input
* Runtime supervisa sin intervenir

---

## Señales de parada (aceptadas)

El sistema **debe responder** a:

* Cierre de ventana UI
* Ctrl+C / SIGINT
* Señal SIGTERM
* Error estructural detectado por Runtime

---

## Shutdown (orden obligatorio)

1. Runtime entra en estado STOPPING
2. Runtime notifica a:

   * Scanners → parar
   * Core → parar
   * UI → cerrar
3. Se drenan / descartan colas
4. Se esperan threads con timeout
5. Se liberan recursos
6. Runtime sale explícitamente

---

## Reglas obligatorias

### Threads

* No se usan threads daemon para lógica principal
* Cada thread:

  * conoce una señal de parada
  * sale voluntariamente

---

### Colas

* No se bloquea indefinidamente en `get()`
* Se usan timeouts o señales de cierre

---

### UI

* El cierre de UI **no mata el proceso**
* UI notifica al Runtime
* Runtime decide el shutdown

---

### Runtime

* Nunca hace `sys.exit()` abrupto
* Nunca deja threads vivos
* Nunca ignora señales del sistema

---

## Alternativas descartadas

Threads daemon
`exit()` desde UI
Dejar al SO “limpiar”
Ignorar SIGINT

Todas producen sistemas frágiles.

---

## Encaje con Architecture Guard

* Runtime mantiene su rol pasivo pero coordinador
* Core y UI no gestionan vida global
* IA no puede “simplificar” el shutdown
* El sistema es predecible

---

## Portabilidad futura

En ESP32:

* startup → `app_main`
* shutdown → control de tasks + watchdog
* mismo orden conceptual

---

## Decisión T9 (formal)

**DT-009 — Ciclo de vida centralizado y apagado limpio**

* Runtime controla startup/shutdown
* Orden explícito
* Señales claras
* Sin threads daemon

**Estado:** Proposed
**Impacto:** Alto
**Reversible:** Difícil
**Riesgo:** Bajo

---

## Confirmación necesaria

Dime solo una:

* **“DT-009 aprobado”** → pasamos a T10 (política de testing y validación)
* **“Quiero simplificar shutdown”** → lo revisamos
* **“Dudas sobre señales”** → las aclaramos

No avanzo hasta que lo confirmes.
