# 2: Containers

En este nivel definimos los contenedores internos del sistema, sus responsabilidades, interfaces y relaciones, sin entrar aún en clases ni funciones. El objetivo es hacer imposible mezclar capas.

## 1 Contenedores definidos
### 1.2 Scanner Container

- Responsabilidad

    - Adquirir observaciones del entorno (WiFi, BLE, Simulador).
    - Normalizar datos crudos a Observation.

- Incluye

    - WiFi Scanner
    - BLE Scanner
    - Sim Scanner (obligatorio)

- Expone

    - Emisión de Observation (stream/eventos).

- No hace
    - No clasifica dispositivos.
    - No dibuja.
    - No mantiene estado agregado.

### 1.3 Core / Tracking Container

- Responsabilidad

    - Fusión de observaciones.
    - Tracking de targets.
    - Filtrado RSSI.
    - Asignación de ángulo/radio.
    - Clasificación heurística.
    - Gestión de estados (active/stale/gone).

- Incluye

    - Modelos (Observation, Target, Snapshot)
    - Tracker
    - Classifier
    - Mapping (RSSI→radio, ID→ángulo)
    - Configuración central

- Expone

    - Snapshot inmutable para consumo de UI.

- No hace

    - No accede a hardware.
    - No dibuja.
    - No gestiona threads/UI loop.

### 1.4 UI / Presentation Container

- Responsabilidad

    - Renderización del radar.
    - Animación de sweep.
    - HUD / panel de estado.
    - Gestión de inputs de usuario (teclas).

- Incluye

    - Radar View
    - HUD
    - Theme (colores, símbolos)
    - Input handler

- Expone

    - Eventos de control (zoom, filtros, selección).

- No hace

    - No escanea.
    - No modifica Target.
    - No aplica lógica de negocio.

### 1.5 Runtime / Orchestration Container

- Responsabilidad

    - Arranque y parada del sistema.
    - Orquestación de loops (scanners, tracker, UI).
    - Gestión de colas/eventos.
    - Configuración del modo (real/simulador).

- Incluye

    - Event Bus / Queues
    - Scheduler (threads o async; se decidirá después)
    - Lifecycle manager

- Expone

    - Ninguna API de dominio; solo cablea contenedores.

- No hace

    - No lógica de dominio.
    - No render.
    - No scanning directo.

## 2 Relaciones entre contenedores
```mermaid
graph TD
    Scanner["Scanner Container<br/">(WiFi / BLE / Sim)]
    Core["Core / Tracking Container"]
    UI["UI / Presentation Container"]
    Runtime["Runtime / Orchestration Container"]

    Scanner -->|Observation events| Core
    Core -->|Snapshot (read-only)| UI

    Runtime -.->|wires / lifecycle| Scanner
    Runtime -.->|wires / lifecycle| Core
    Runtime -.->|wires / lifecycle| UI
```
- Regla absoluta

    - Dependencias unidireccionales.
    - UI solo lee.
    - Scanners solo emiten.
    - Core solo transforma.

## 3 Interfaces entre contenedores (contratos de alto nivel)
- `Scanner → Core`

    - Canal: Queue / Event Stream
    - Tipo: Observation
    - Frecuencia: variable (configurable)
    - Backpressure: soportado (cola con límite)

- `Core → UI`

    - Canal: Snapshot pull o push (decisión pendiente)
    - Tipo: Snapshot inmutable
    - Frecuencia: desacoplada del scanning

- `UI → Runtime`

    - Canal: eventos de control
    - Tipo: comandos simples (zoom+, filter=BLE, select_next)

## 4 Decisiones explícitas (pre-ADR)

- Separación en 4 contenedores (no 3): Runtime es obligatorio para evitar acoplamientos.

- Snapshots inmutables para evitar condiciones de carrera.

- Simulador como scanner de primera clase, no herramienta de test.

Estas decisiones se formalizarán luego como ADR.

## 5 Lo que NO se decide aún

- Threads vs asyncio.

- Framework gráfico concreto.

- Frecuencia exacta de loops.

- Persistencia (si existe).

Eso es deliberado.