Perfecto.
A continuación tienes **ADR-006 completo**, cerrado, normativo y sin ambigüedades.
**Solo ADR-006**, listo para **copiar y pegar**.

---

# ADR-006 — El **Runtime** actúa como **orquestador pasivo**, sin lógica de dominio

**Estado:** Accepted
**Fecha:** *25/12/2025*
**Decisores:** *Nehonar / Radar Dragon ball*
**Alcance:** Runtime / Scanner / Core / UI

---

## Contexto

El sistema necesita un componente responsable de:

* arrancar y detener el sistema,
* inicializar contenedores,
* cablear flujos de datos,
* gestionar ciclos de vida y concurrencia.

En muchos sistemas, este componente (“main”, “app”, “manager”) termina:

* acumulando lógica de negocio,
* tomando decisiones de dominio,
* manipulando datos directamente,
* o convirtiéndose en un *God Object*.

Esto provoca:

* acoplamiento fuerte entre capas,
* duplicación de lógica,
* dificultad para testear,
* imposibilidad de razonar sobre el sistema,
* y agentes de IA que “arreglan cosas” en el lugar incorrecto.

---

## Decisión

Se decide que:

> **El Runtime es un orquestador pasivo, no un componente de dominio.**

El Runtime:

* **coordina**, pero no decide;
* **conecta**, pero no transforma;
* **inicia y detiene**, pero no interpreta datos.

Toda lógica funcional pertenece exclusivamente al **Core** o a la **UI**, según corresponda.

---

## Responsabilidades permitidas del Runtime

El Runtime **puede**:

1. Crear instancias de:

   * Scanners
   * Core / Tracker
   * UI

2. Configurar:

   * colas / buses de eventos,
   * parámetros globales,
   * modos de ejecución (simulador / real).

3. Gestionar:

   * hilos, tareas o bucles asíncronos,
   * arranque, parada y limpieza,
   * manejo de señales del sistema (exit, shutdown).

4. EncaminAR:

   * `Observation` desde Scanners al Core,
   * `Snapshot` desde Core a UI,
   * comandos desde UI a quien corresponda.

---

## Responsabilidades explícitamente prohibidas

El Runtime **NO puede**:

* Clasificar Targets.
* Filtrar RSSI.
* Calcular ángulos o radios.
* Decidir qué Target es “más cercano”.
* Interpretar Observations.
* Acceder o modificar estado interno del Core.
* Renderizar UI.
* Contener reglas de negocio.

Si el Runtime necesita “entender” datos,
**la lógica está en el lugar equivocado**.

---

## Alternativas consideradas

### Alternativa A — Runtime con lógica de negocio

* Rechazada

**Motivos**

* God Object.
* Difícil de testear.
* Rompe separación de capas (ADR-001).
* IA tiende a añadir lógica aquí “porque es fácil”.

---

### Alternativa B — Runtime inexistente (todo en `main`)

* Rechazada

**Motivos**

* Mezcla de responsabilidades.
* Código frágil.
* Dificultad para escalar o portar.

---

### Alternativa C — Runtime que modifica datos “ligeramente”

* Rechazada

**Motivos**

* No existe modificación “ligera” segura.
* Abre la puerta a corrupción de estado.
* Dificulta el razonamiento del sistema.

---

## Consecuencias

### Positivas

* Arquitectura clara y mantenible.
* Lógica localizada y testeable.
* Portabilidad a otros entornos (ESP32).
* IA no puede introducir lógica fuera del Core.
* Debug más simple.

### Negativas

* El Runtime puede parecer “simple” o “tonto”.
* Requiere disciplina para no usarlo como atajo.

Estas consecuencias son **aceptadas explícitamente**.

---

## Relación con contratos y ADR previos

Este ADR:

* Refuerza ADR-001 (separación de capas).
* Refuerza ADR-004 (desacoplamiento Core–UI).
* Refuerza contratos de capas (`/docs/contracts/layer-contracts.md`).

Cualquier implementación que:

* tome decisiones de dominio en Runtime,
* modifique datos que no le pertenecen,
* o duplique lógica del Core,

**viola este ADR**.

---

## Regla derivada (normativa)

> El Runtime **coordina el sistema**,
> pero **no sabe qué significa lo que coordina**.

---

## Cierre

Este ADR deja explícito que el Runtime es **infraestructura**, no dominio, y completa el conjunto mínimo de decisiones arquitectónicas necesarias para programar sin ambigüedades.
