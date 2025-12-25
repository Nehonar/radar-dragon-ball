# Decisiones Técnicas — Paso T5

## **Estructura del proyecto y convenciones de naming**

Esta decisión parece “menor”, pero en realidad es **crítica** para:

* que la arquitectura se mantenga sola,
* que la IA no mezcle capas,
* que el proyecto escale sin desorden,
* y que el port a ESP32 sea natural.

---

## Problema a resolver

Si no fijamos **estructura y nombres**:

* las capas se difuminan,
* aparecen imports indebidos,
* el Runtime se convierte en “cajón de sastre”,
* la IA crea módulos “helper” que rompen contratos.

La estructura **es parte del Architecture Guard**.

---

## Principios obligatorios

1. **Una carpeta = un contenedor**
2. **Los nombres reflejan responsabilidad, no tecnología**
3. **Nada “genérico”** (`utils`, `helpers`, `common`)
4. **El Core no depende de frameworks**
5. **La UI no depende de Scanners**

---

## Estructura propuesta (Python)

```
rf_radar/
├── app/
│   └── runtime.py
│
├── scanners/
│   ├── wifi_scanner.py
│   ├── ble_scanner.py
│   └── sim_scanner.py
│
├── core/
│   ├── models.py
│   ├── tracker.py
│   ├── classifier.py
│   ├── mapping.py
│   ├── snapshot.py
│   └── config.py
│
├── ui/
│   ├── main_view.py
│   ├── radar_view.py
│   ├── hud.py
│   ├── input.py
│   └── theme.py
│
├── infrastructure/
│   ├── queues.py
│   └── logging.py
│
├── main.py
└── __init__.py
```

---

## Justificación por carpeta

### `scanners/`

* **Solo adquisición**
* Un archivo = una fuente
* No importa quién consume

* Refuerza ADR-001
* Facilita añadir nuevos scanners

---

### `core/`

* **Dominio puro**
* Sin dependencias gráficas
* Sin dependencias de hardware

* Facilita test
* Facilita portabilidad

---

### `ui/`

* **Presentación**
* Render + input
* Consume `Snapshot`

* Encaja con Pygame
* Evita lógica accidental

---

### `app/`

* **Orquestación**
* Arranque, parada, wiring

* Runtime pasivo (ADR-006)

---

### `infrastructure/`

* Infraestructura compartida **no de dominio**
* Colas, logging, configuración técnica

* Evita contaminar Core
* Alternativa a `utils` (prohibido)

---

## Convenciones de naming (normativas)

### Archivos

* `*_scanner.py` → solo scanners
* `*_view.py` → solo UI
* `tracker.py` → lógica de tracking
* `mapping.py` → RSSI → r, id → θ

---

### Clases / tipos

* `Observation`, `Target`, `Snapshot` → dominio
* `Scanner` → productor
* `Runtime` → orquestador

---

### Prohibiciones explícitas

`utils.py`
`helpers.py`
`common.py`
`manager.py` (salvo Runtime explícito)

Motivo:

> Los nombres vagos destruyen arquitectura.

---

## Encaje con Architecture Guard

Esta estructura:

* **impide imports ilegales**
* **hace visibles las violaciones**
* **guía a la IA por el camino correcto**

Si un archivo:

* necesita acceder a otra capa,
* pero “no hay sitio donde ponerlo”,

esa es la señal de que **la decisión es incorrecta**.

---

## Decisión T5 (formal)

**DT-005 — Estructura de proyecto por contenedores**

* Una carpeta = un contenedor
* Naming explícito
* Sin módulos genéricos
* Infraestructura separada del dominio

**Estado:** Proposed
**Impacto:** Alto
**Reversible:** Difícil
**Riesgo:** Bajo