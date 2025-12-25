# Architecture Guard — RF Presence Radar

**Estado:** Activo
**Alcance:** Todo el proyecto
**Cumplimiento:** Obligatorio (humano e IA)

---

## 1. Propósito

Este documento define las **reglas arquitectónicas no negociables** del proyecto **RF Presence Radar**.

Su objetivo es:

* preservar la arquitectura acordada,
* evitar degradación progresiva del diseño,
* impedir “optimizaciones” incorrectas,
* y garantizar que cualquier contribución (incluida IA) respete el sistema completo.

Si una solución **viola alguna regla de este documento**,
**la solución es inválida**, aunque funcione.

---

## 2. Regla de oro

> **Ningún componente puede asumir responsabilidades fuera de su contenedor.**

---

## 3. Contenedores y responsabilidades (resumen vinculante)

### Scanner

* Obtiene señales (WiFi / BLE / Simulador)
* Emite `Observation`
* No mantiene estado agregado
* No conoce UI ni Core

---

### Core / Tracking

* Única capa con lógica de dominio
* Agrega `Observation` → `Target`
* Produce `Snapshot` inmutable
* Define clasificación, filtros y mapeos
* No accede a hardware
* No renderiza

---

### UI / Presentation

* Renderiza radar y HUD
* Consume `Snapshot`
* Gestiona inputs del usuario
* No modifica estado
* No clasifica
* No accede a Scanners ni Core internos

---

### Runtime / Orchestration

* Inicializa y conecta componentes
* Gestiona ciclo de vida y concurrencia
* EncaminA eventos
* **No contiene lógica de dominio**
* **No interpreta datos**

---

## 4. Dirección obligatoria de dependencias

```
Scanner → Core → UI
Runtime → (Scanner, Core, UI)
```

No se permiten dependencias inversas
No se permiten atajos “temporales”

---

## 5. Reglas de datos (inmutables)

### Observation

* Representa una detección puntual
* Es inmutable
* Contiene RSSI crudo
* No contiene lógica ni derivados

---

### Target

* Representa estado agregado
* Ángulo fijo durante toda su vida
* Radio derivado solo de RSSI filtrado
* No es mutable desde UI

---

### Snapshot

* Es inmutable
* Representa un instante coherente
* Es la **única** forma de comunicar Core → UI

---

## 6. Reglas del radar (NO negociables)

* El radar es **estrictamente 2D**
* No existe eje Z
* No existe profundidad
* No existe pseudo-3D

### Posicionamiento

* Cada Target tiene:

  * una **dirección fija (θ)**
  * una **distancia variable (r)**

```
x = r · cos(θ)
y = r · sin(θ)
```

* RSSI más alto → más cerca del centro
* RSSI más bajo → más lejos
* El Target **nunca cambia de dirección**
* El movimiento es **solo radial**

Si un Target:

* rota,
* orbita,
* cambia de cuadrante,

**es un bug arquitectónico**.

---

## 7. RSSI (regla crítica)

* RSSI es **proximidad relativa**
* RSSI **NO es distancia física**
* Nunca se calculan metros
* Nunca se muestran metros
* Nunca se calibra entorno

Cualquier campo tipo:

* `distance_m`
* `meters`
* `real_distance`

Está prohibido.

---

## 8. Snapshots y concurrencia

* Core y UI están desacoplados
* UI solo ve Snapshots
* No hay locks compartidos
* No hay acceso “en vivo” al Core
* El Core nunca espera a la UI

---

## 9. Simulador (obligatorio)

* El simulador es un Scanner más
* Usa los mismos contratos
* El sistema debe funcionar **solo con simulador**
* UI y Core no distinguen origen real/simulado

Si el sistema:

* no arranca sin hardware
* necesita WiFi/BLE para funcionar

**está mal diseñado**.

---

## 10. Runtime (prohibiciones explícitas)

El Runtime **NO puede**:

* clasificar Targets
* filtrar RSSI
* calcular ángulos o radios
* decidir lógica de dominio
* interpretar Observations

Si el Runtime “entiende” datos:
la lógica está mal ubicada.

---

## 11. Uso obligatorio con IA

Antes de escribir código, cualquier agente de IA debe:

1. Leer este Architecture Guard
2. Verificar que su solución:

   * respeta separación de capas
   * no introduce lógica indebida
   * no rompe invariantes
3. **Rechazar** su propia solución si viola alguna regla

---

## 12. Regla final

> **El código puede cambiar.
> La arquitectura no.**

---

## 13. Referencias normativas

* `/docs/architecture/c4/`
* `/docs/contracts/`
* `/docs/adr/ADR-001` a `ADR-006`

---

### Fin del Architecture Guard