Perfecto. Continuamos.

A continuación tienes **ADR-005 completo**, en el mismo formato, nivel de rigor y alcance que los anteriores. **Solo ADR-005**, listo para copiar y pegar.

---

# ADR-005 — El **Simulador** es una fuente de datos de **primera clase**

**Estado:** Accepted
**Fecha:** *25/12/2025*
**Decisores:** *Nehonar / Radar Dragon ball*
**Alcance:** Scanner / Core / UI / Runtime

---

## Contexto

El sistema depende de fuentes físicas (WiFi y BLE) que:

* pueden no estar disponibles en todos los entornos,
* dependen del sistema operativo y permisos,
* producen datos no deterministas,
* dificultan el desarrollo visual y la depuración,
* ralentizan la iteración del diseño de UI y lógica.

En muchos proyectos, el simulador:

* se introduce tarde,
* se trata como herramienta de test,
* o se implementa fuera de la arquitectura principal.

Esto provoca:

* divergencia entre código real y simulado,
* UI acoplada a hardware,
* dificultad para depurar comportamientos visuales,
* y agentes de IA que desarrollan contra supuestos incorrectos.

---

## Decisión

Se decide que:

> **El simulador es una fuente de datos de primera clase, equivalente a WiFi y BLE.**

Esto implica que:

* El simulador **es un Scanner más**, no una herramienta externa.
* Emite `Observation` usando **los mismos contratos**.
* El Core y la UI **no distinguen** entre datos reales o simulados.
* El sistema **puede arrancar y funcionar plenamente** sin hardware RF.

---

## Reglas obligatorias

1. **Simetría de contratos**

   * El simulador emite exactamente el mismo tipo de `Observation`.
   * No existen campos “solo para simulador”.

2. **Intercambiabilidad**

   * Runtime puede activar:

     * solo simulador
     * simulador + hardware
     * solo hardware
   * Sin cambios en Core o UI.

3. **Determinismo**

   * El simulador puede operar en modo determinista:

     * seeds fijas
     * patrones reproducibles
   * Permite depuración y validación visual.

4. **Cobertura de escenarios**

   * El simulador debe poder generar:

     * Targets estables
     * aparición/desaparición
     * fluctuaciones de RSSI
     * múltiples Targets con RSSI similar
     * ruido controlado

5. **Paridad funcional**

   * Cualquier cambio en contratos reales **debe reflejarse** en el simulador.
   * El simulador **no puede quedarse atrás**.

---

## Alternativas consideradas

### Alternativa A — Simulador solo para tests

* Rechazada

**Motivos**

* Divergencia de caminos de código.
* UI desarrollada contra supuestos irreales.
* Baja calidad visual final.

---

### Alternativa B — Mocking dentro del Core

* Rechazada

**Motivos**

* Rompe separación de capas (ADR-001).
* Introduce lógica de test en producción.
* Dificulta portabilidad.

---

### Alternativa C — Simulador integrado en la UI

* Rechazada

**Motivos**

* UI dependiente de dominio.
* Violación de contratos.
* Imposible de reutilizar.

---

## Consecuencias

### Positivas

* Desarrollo rápido y predecible.
* UI y Core robustos incluso sin hardware.
* Reproducción exacta de escenarios complejos.
* IA puede trabajar sin acceso a RF real.
* Portabilidad inmediata a ESP32.

### Negativas

* Más código inicial.
* Disciplina para mantener paridad.

Estas consecuencias son **aceptadas explícitamente**.

---

## Relación con contratos

Este ADR:

* Refuerza los contratos `Observation`.
* Refuerza el invariante “Simulador obligatorio”.
* Obliga a que cualquier pipeline acepte datos simulados.

Cualquier implementación que:

* trate el simulador como excepción,
* introduzca ramas especiales en Core o UI,
* o asuma siempre hardware real,

**viola este ADR**.

---

## Regla derivada (normativa)

> Si el sistema no funciona con el simulador,
> **el sistema no está correctamente diseñado**.

---

## Cierre

Este ADR garantiza que el sistema sea **desarrollable, depurable y portable** desde el primer día.
