# ADR-004 — Uso de **Snapshots inmutables** para desacoplar Core y UI

**Estado:** Accepted
**Fecha:** *25/12/2025*
**Decisores:** *Nehonar / Radar Dragon ball*
**Alcance:** Core / UI / Runtime

---

## Contexto

El sistema procesa señales asíncronas (WiFi, BLE, simulador) y debe renderizar una UI reactiva y estable.

Problemas habituales en sistemas similares:

* la UI accede a estructuras internas del Core,
* se comparten objetos mutables entre threads/loops,
* se introducen locks complejos,
* aparecen condiciones de carrera, parpadeos o estados incoherentes,
* agentes de IA “optimizan” accediendo directamente al estado interno.

Estos problemas:

* degradan la estabilidad visual,
* hacen el sistema frágil ante cambios,
* dificultan el port a otros entornos (p. ej. ESP32).

---

## Decisión

Se decide que:

> **La comunicación entre Core y UI se realiza exclusivamente mediante Snapshots inmutables.**

Un **Snapshot** representa:

* una **vista coherente del estado** en un instante concreto,
* preparada para render,
* sin referencias mutables al estado interno del Core.

La UI:

* **solo consume Snapshots**,
* **no accede** a estructuras internas,
* **no solicita cambios de estado** al Core.

---

## Reglas obligatorias

1. **Inmutabilidad**

   * Un Snapshot no se modifica una vez creado.
   * La UI no puede alterar Targets, listas ni estadísticas.

2. **Aislamiento**

   * El Snapshot **no contiene referencias** a objetos mutables del Core.
   * Los Targets dentro del Snapshot son copias o vistas inmutables.

3. **Unidireccionalidad**

   * Core → UI: datos (Snapshots)
   * UI → Runtime: comandos
   * UI **nunca** llama al Core para “pedir estado”.

4. **Desacoplamiento temporal**

   * El ritmo de creación de Snapshots **no depende** del FPS de la UI.
   * La UI puede renderizar el último Snapshot disponible.

5. **No bloqueo**

   * El Core **no espera** a que la UI consuma un Snapshot.
   * La UI **no bloquea** esperando nuevos datos.

---

## Alternativas consideradas

### Alternativa A — UI accede directamente a estado del Core

* Rechazada

**Motivos**

* Condiciones de carrera.
* Locks complejos.
* UI frágil y difícil de portar.
* Rompe separación de capas (ADR-001).

---

### Alternativa B — Estado mutable compartido con locks

* Rechazada

**Motivos**

* Alto coste cognitivo.
* Riesgo de deadlocks.
* Difícil de mantener con IA.
* Innecesario para este dominio.

---

### Alternativa C — Mensajes incrementales (diffs)

Considerada, pero descartada por ahora

**Motivos**

* Complejidad prematura.
* Dificulta simulador.
* Dificulta render simple y robusto.

---

## Consecuencias

### Positivas

* UI simple y segura.
* Render estable sin parpadeos incoherentes.
* Core libre de preocupaciones de presentación.
* Fácil portabilidad a sistemas con recursos limitados.
* IA no puede romper estado compartido.

### Negativas

* Copias adicionales de datos.
* Ligero overhead de memoria/CPU.

Estas consecuencias son **aceptadas explícitamente**.

---

## Relación con contratos

Este ADR:

* Refuerza `/docs/contracts/data-contracts.md` (`Snapshot`)
* Refuerza `/docs/contracts/layer-contracts.md` (Core → UI)
* Garantiza invariantes de:

  * no bloqueo
  * inmutabilidad
  * separación de responsabilidades

Cualquier implementación que:

* exponga estado mutable del Core,
* permita a la UI modificar Targets,
* o dependa de locks entre Core y UI,

**viola este ADR**.

---

## Regla derivada (normativa)

> La UI **nunca ve el sistema “en vivo”**,
> solo ve **fotografías coherentes** del estado.

---

## Cierre

Este ADR garantiza la **robustez temporal y estructural** del sistema y es obligatorio para cualquier implementación presente o futura.
