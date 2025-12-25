# Decisiones Técnicas — Paso T3

## Fuentes de datos RF en Ubuntu (WiFi / BLE) y estrategia de permisos

Aquí fijamos **cómo** se obtienen los datos RF en el prototipo Python, **sin romper la arquitectura** y **sin asumir privilegios peligrosos**.

Esta decisión condiciona:

* qué tan fácil es ejecutar el prototipo
* qué datos reales obtienes
* cómo se comporta el simulador
* la portabilidad futura

---

## Requisitos técnicos (derivados de arquitectura)

Las fuentes RF deben:

* producir `Observation` conforme al contrato
* funcionar en **threads independientes**
* no bloquear UI ni Core
* poder desactivarse sin romper el sistema
* convivir con el simulador

Además:

* el sistema **debe funcionar sin RF real** (ADR-005)
* los scanners **no hacen lógica**, solo observan

---

## Opción 1 — WiFi en Ubuntu

### Realidad técnica (honesta)

En Linux, el escaneo WiFi:

* **sí es posible**
* **pero** depende de permisos
* y de herramientas externas

### Alternativas WiFi evaluadas

#### A) `iw` / `iw dev scan`

* Devuelve BSSID, RSSI, canal, SSID
* Requiere:

  * root
  * o capabilities (`CAP_NET_ADMIN`)

✔ Datos de buena calidad
Requiere permisos elevados

---

#### B) `nmcli dev wifi list`

* Funciona como usuario normal (a veces)
* RSSI disponible
* Menos información

✔ Fácil de usar
✔ Más “user-friendly”
Menos control

---

### Decisión WiFi

> **Usar `nmcli` como fuente WiFi primaria**
> y permitir `iw` solo como opción avanzada/documentada.

Motivo:

* menos fricción
* menos permisos
* más portable
* suficiente para radar visual

---

## Opción 2 — BLE en Ubuntu

### Alternativas BLE evaluadas

#### A) `bleak` (Python)

* Biblioteca moderna
* Funciona sin root
* Acceso a RSSI y advertising
* Soporta Linux bien

✔ Limpio
✔ Idiomático en Python
✔ Perfecto para threads
✔ Ideal para este proyecto

---

#### B) `hcitool` / `bluetoothctl`

* Obsoletos
* CLI parsing
* Menos fiables

Rechazados

---

### Decisión BLE

> **Usar `bleak` como fuente BLE oficial.**

---

## Estrategia de permisos (muy importante)

### Principio

> **El prototipo debe funcionar como usuario normal.**

Reglas:

* No requerir `sudo` por defecto
* No modificar capabilities automáticamente
* Documentar claramente opciones avanzadas

### Escenarios permitidos

* Sin WiFi → simulador + BLE
* Sin BLE → simulador + WiFi
* Sin ambos → solo simulador

---

## Encaje con arquitectura

* Cada fuente RF = **Scanner independiente**
* Emiten `Observation`
* Runtime decide qué scanners arrancar
* Core y UI no saben de dónde vienen los datos

---

## Decisión T3 (formal)

**DT-003 — Fuentes RF en Ubuntu**

* WiFi: `nmcli` (primario)
* BLE: `bleak`
* Simulador: obligatorio
* Permisos elevados: opcionales, nunca requeridos

**Estado:** Proposed
**Impacto:** Medio
**Reversible:** Sí
**Riesgo:** Bajo
