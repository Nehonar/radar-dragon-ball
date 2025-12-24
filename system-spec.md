Paso 1 — Definición de arquitectura: Alcance, requisitos y límites

A continuación dejo una especificación de arquitectura “nivel 0” (contexto completo) para el Radar de Presencia RF implementado primero en Python. Este paso no incluye código; establece el contrato del sistema para que cualquier agente pueda trabajar sin romperlo.

1.1 Objetivo del sistema

Construir una aplicación de escritorio (Python) que:

Escanee el entorno cercano mediante WiFi y BLE (cuando el hardware/OS lo permita).

Agregue observaciones de dispositivos (“targets”) y estime su proximidad relativa usando RSSI.

Renderice una UI tipo radar (barrido circular) en una ventana, con simbología retro y panel de detalle.

Sea robusta y extensible: separar adquisición de datos, procesamiento y UI para poder portar luego a ESP32.

1.2 Resultados esperados (salidas)

Vista principal radar (2D) con:

Centro fijo (el “scanner”).

Targets como puntos con posición radial derivada de RSSI y ángulo asignado de forma estable.

“Sweep” o barrido animado.

Panel/overlay de estado:

Conteo de targets por categoría (BLE/WiFi).

Target “seleccionado” o “más cercano” con RSSI filtrado, tipo estimado, “edad” (tiempo desde última detección).

Registro (log) opcional para depuración:

Eventos de aparición/desaparición.

Estadísticas de escaneo.

1.3 Requisitos funcionales

Ingesta de observaciones

El sistema recibe “observations” con campos mínimos:

source: wifi | ble

id: identificador estable (p.ej. BSSID/MAC, o hash si hay randomización)

rssi: valor RSSI en dBm (int)

timestamp: epoch o monotonic

metadata: dict (SSID, nombre BLE, canal, fabricante estimado, etc.)

Fusión y tracking

Mantener una tabla de “targets” (estado agregado por id):

RSSI filtrado (suavizado)

última vez visto

contador de observaciones

clasificación (móvil/portátil/AP/desconocido) con reglas deterministas

estado de vida: active / stale / gone

Mapeo RSSI → distancia visual

Función determinista y parametrizable (clamp + normalización):

RSSI fuerte (p.ej. -30) cerca del centro

RSSI débil (p.ej. -90) cerca del borde

Debe soportar “zoom” (cambiar rango RSSI).

Asignación de ángulo estable

Cada target recibe un ángulo fijo/estable para evitar saltos:

derivado de hash del id (o técnica equivalente)

no depende del orden de llegada

Opción de “jitter” controlado para “vida” visual sin caos.

Render / UI

Loop de render independiente del loop de escaneo.

FPS moderado (p.ej. 20–30 en PC, configurable).

Barrido (sweep) con velocidad configurable.

No bloquear UI por escaneo.

1.4 Requisitos no funcionales

Separación estricta por capas (para evitar que cambios rompan todo):

Adquisición (scanners) no conoce UI.

UI no hace scanning directo.

Núcleo (tracker) no depende de librerías gráficas.

Determinismo y testabilidad:

tracker y mapeos con funciones puras donde sea posible.

Degradación elegante:

Si BLE o WiFi no está disponible, el sistema sigue con el resto.

Modo “simulador” para desarrollo sin hardware.

Portabilidad:

Debe correr en Linux (Ubuntu). Windows/Mac opcional.

Privacidad / seguridad:

No guardar identificadores crudos por defecto (opcional “anonimizar”).

No intentar “identificar personas”, solo dispositivos.

1.5 Límites y supuestos (muy importante)

RSSI es proximidad relativa, no distancia real.

En algunos OS, escaneo WiFi puede requerir permisos y/o devolver info limitada.

BLE puede dar MAC randomizada; se aceptará estabilidad parcial.

No se realizará “tracking por movimiento” real; solo proximidad.

1.6 Arquitectura propuesta (alto nivel)
Componentes (módulos) y responsabilidades

scanners/

wifi_scanner: produce observations WiFi

ble_scanner: produce observations BLE

sim_scanner: genera observations sintéticas reproducibles (para tests/UI)

Contrato: cada scanner emite Observation a un bus/cola.

core/

models: dataclasses Observation, Target, enums

tracker: fusión, estados, expiración, selección “nearest”

classifier: reglas de tipo (AP vs móvil vs portátil)

mapping: RSSI→radio, id→ángulo, normalizaciones

config: parámetros del sistema (timeouts, rangos, FPS, etc.)

app/

runtime: orquestación (threads/async), colas, lifecycle

events: bus simple (Queue) y mensajes internos

ui/

radar_view: render del radar

hud: panel inferior (estado/target seleccionado)

input: teclas para zoom/filtros/modes

theme: colores, fuentes, símbolos (retro)

Flujos (dataflow)

Scanners → (Queue: Observations) → Tracker → (Snapshot de Targets) → UI Render

Nunca al revés.

1.7 Contratos de datos (para que nadie rompa nada)
Observation

source: Literal["wifi","ble","sim"]

id: str (estable dentro de la sesión)

rssi: int

ts: float

meta: dict

Target

id: str

source_mask: set (wifi/ble)

rssi_raw_last: int

rssi_filt: float

angle_deg: float

radius_norm: float (0..1)

last_seen_ts: float

state: active|stale|gone

kind: mobile|laptop|ap|unknown

label: str (para UI, opcional y anonimizable)

Snapshot

targets: list[Target] (solo activos/stale según config)

stats: counters

selected_id: Optional[str]

now_ts: float

1.8 Decisiones de diseño (cerradas por ahora)

Modelo por eventos (cola) en vez de llamadas directas.

Tracker produce snapshots inmutables para UI (evita condiciones de carrera).

Config centralizado (un solo sitio).

Modo simulador incluido desde el inicio (reduce fricción y acelera el diseño visual).