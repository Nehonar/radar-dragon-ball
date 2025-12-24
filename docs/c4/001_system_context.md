# 1: System Context
## 1 Propósito del diagrama C1

Definir, a nivel de contexto, qué es el sistema, quién interactúa con él, y qué dependencias externas existen, sin entrar en módulos internos.

## 2 Sistema (System of Interest)

Nombre: RF Presence Radar (Python Prototype)
Responsabilidad: Escanear señales WiFi/BLE cercanas, estimar proximidad relativa mediante RSSI y presentarlo en una UI tipo radar.

## 3 Actores (Personas / Roles)

- Operador (User)
- Inicia/para la aplicación.
- Observa el radar.
- Cambia modos (zoom, filtros, selección).
- Interpreta proximidad como señal de “cerca/lejos”.

## 4 Sistemas externos y dependencias

- Sistema Operativo (Ubuntu/Linux)
- Proporciona acceso a interfaces WiFi/BLE y permisos.
- Impacta disponibilidad de datos (limitaciones y permisos).
- Adaptador WiFi del equipo
- Fuente física de escaneo WiFi (APs/Beacons/Canales/RSSI).
- Adaptador Bluetooth del equipo
- Fuente física de escaneo BLE (advertisements/RSSI).
- Dispositivos cercanos (Targets)
- Emisores BLE y/o WiFi (móviles, portátiles, routers, etc.).
- Pueden randomizar identificadores y variar potencia.
- Modo Simulador (opcional, externo al entorno físico)
- Fuente sintética de observations para desarrollo y pruebas sin hardware.

## 5 Interacciones (alto nivel)

`Operador → Sistema`: control (modo, zoom, filtros, salida)

`Sistema → OS + Adaptadores`: solicitudes de escaneo, recepción de resultados.

`Sistema → Operador`: renderización radar + estado + logs.

`Dispositivos cercanos → Adaptadores → Sistema`: emisiones detectables (WiFi/BLE) con RSSI.

## 6 Límites del sistema (scope boundary)

- Incluido:

    - Visualización radar

    - Tracking y filtrado RSSI

    - Clasificación heurística simple

    - Simulador interno para pruebas

- Excluido (explícitamente fuera de alcance):

    - Geolocalización en metros

    - Identificación personal / fingerprinting avanzado

    - Captura de tráfico, sniffing profundo o decontenido

    - Almacenamiento persistente de identificadores por defecto

## 7 Representación textual tipo C4 (C1)

[Person] Operador usa → [System] RF Presence Radar

[System] RF Presence Radar obtiene señales desde → [External System] OS/Drivers WiFi

[System] RF Presence Radar obtiene señales desde → [External System] OS/Drivers Bluetooth

[External System] Dispositivos cercanos emiten → WiFi/BLE → detectado por el sistema

[External System] Simulador (opcional) alimenta → [System] RF Presence Radar con observations