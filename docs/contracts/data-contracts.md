# Contratos formales

# 1 Contratos de datos (Data Contracts)

### 1.1 `Observation` (contrato de entrada al Core)

**Propósito**
Representar **una detección puntual**, sin estado agregado.

**Campos obligatorios**

* `source`: enum `{wifi | ble | sim}`
* `id`: `string`
* `rssi`: `int` (dBm)
* `ts`: `float` (timestamp monotónico o epoch)
* `meta`: `dict` (opcional, no estructural)

**Reglas**

* `Observation` es **inmutable**
* `id` **no se reinterpreta** en capas posteriores
* `rssi` es **valor crudo**, sin filtrar
* `meta` **nunca es requerido** para lógica crítica

**Prohibiciones**

* No añadir campos derivados (distancia, ángulo, tipo)
* No almacenar estado histórico

---

### 1.2 `Target` (estado agregado interno del Core)

**Propósito**
Representar un **dispositivo rastreado en el tiempo**.

**Campos obligatorios**

* `id`: `string`
* `source_mask`: `set`
* `rssi_raw_last`: `int`
* `rssi_filt`: `float`
* `angle_deg`: `float`
* `radius_norm`: `float` ∈ `[0,1]`
* `last_seen_ts`: `float`
* `state`: enum `{active | stale | gone}`
* `kind`: enum `{mobile | laptop | ap | unknown}`

**Reglas**

* `angle_deg` es **estable** durante la vida del Target
* `radius_norm` **solo** depende de RSSI filtrado
* `state` depende **solo del tiempo**, no del render

**Prohibiciones**

* La UI no puede modificar `Target`
* No se recalcula ángulo en cada observación

---

### 1.3 `Snapshot` (contrato Core → UI)

**Propósito**
Proveer una **vista coherente e inmutable** para render.

**Campos obligatorios**

* `targets`: lista de `Target`
* `stats`: contadores agregados
* `selected_id`: `string | null`
* `now_ts`: `float`

**Reglas**

* Snapshot es **inmutable**
* Representa **un instante**
* UI **solo puede leer**

**Prohibiciones**

* No referencias mutables a `Target` internos
* No llamadas al Core desde la UI para “pedir cambios”

---

# 2 Contratos entre capas (Layer Contracts)

## 2.1 Scanner → Core

**Contrato**

* Comunicación **unidireccional**
* Medio: cola/eventos
* Tipo: `Observation`

**Garantías**

* El Scanner **no conoce** al Core
* El Core **no controla** el ritmo del Scanner

**Invariantes**

* Una Observation **no se pierde silenciosamente**
* Si la cola está llena → descartar explícito + métrica

---

## 2.2 Core → UI

**Contrato**

* El Core expone **Snapshots**
* La UI **no muta estado**

**Garantías**

* Snapshot siempre consistente
* UI puede renderizar sin locks

**Invariantes**

* Core **nunca bloquea** esperando a UI
* UI **nunca accede** a estructuras internas

---

## 2.3 UI → Runtime

**Contrato**

* UI emite **comandos**, no acciones
* Runtime decide cómo aplicar

**Ejemplos**

* `zoom_in`
* `toggle_ble`
* `select_next`

**Invariantes**

* UI **no ejecuta lógica**
* Runtime **no altera dominio**

---

# 3 Contratos de invariantes globales (NO negociables)

Estos son los que **evitan que el sistema se degrade con el tiempo**.

### Invariante 1 — Dirección de dependencias

```
Scanner → Core → UI
Runtime ─┬─→ Scanner
         ├─→ Core
         └─→ UI
```

Ninguna dependencia inversa está permitida.

---

### Invariante 2 — UI es pura presentación

* UI **no decide**
* UI **no filtra**
* UI **no clasifica**

Si la UI “necesita” lógica → esa lógica **no pertenece a la UI**.

---

### Invariante 3 — RSSI ≠ distancia real

* RSSI es **proximidad relativa**
* Ningún módulo puede asumir metros
* Cualquier intento de “calibrar distancia real” es **out of scope**

---

### Invariante 4 — Estabilidad visual

* Un `Target` no “salta” de posición angular
* El movimiento radial es **suavizado**
* El parpadeo es intencional, no ruido

---

### Invariante 5 — Simulador es ciudadano de primera clase

* El sistema **debe funcionar** sin WiFi ni BLE
* El simulador **usa los mismos contratos**
* UI no distingue origen real vs simulado

---

# 4 Contratos de evolución (para IA y humanos)

### Permitido

* Añadir nuevos scanners
* Añadir nuevos campos **no obligatorios** a `meta`
* Añadir nuevos modos de render
* Ajustar mapeos RSSI → radio

### Prohibido

* Cambiar significado de `rssi`
* Reinterpretar `id`
* Añadir estado mutable a UI
* Acoplar Scanner con UI

