# Runbook Operativo: Modelación de Dispersión Atmosférica con AERMOD (ZMVM)

Este documento registra el flujo técnico completo para estimar concentraciones hiperlocales de PM2.5 (a 1.5 m de altura) provenientes de fuentes fijas industriales, acoplando topografía (AERMAP), meteorología de capa límite (AERMET), perfiles temporales de emisión (EMISFACT) y salidas agregadas (PLOTFILE) o de alta resolución (POSTFILE).

## 1. Entorno y Estructura del Repositorio
* **Binarios compilados:** AERMOD v24142, AERMET y AERMAP compilados nativamente en Fortran (gfortran, Apple Silicon / compatible con Linux). Automatización en Python (entorno Conda `aermod-lab` / `thesis-cdmx`).
* **Estructura de carpetas:**
  * `02-data/raw/` — Insumos crudos (RETC, PLANEA, curvas energéticas, reportes MDA de CENACE, DEMs).
  * `02-data/processed/` — Salidas intermedias (`aermap_out/`, `aermet_out/`, `emisfact_mhrdow/`, `cenace_cfe/`).
  * `03-analysis/aermod_bin/` — Ejecutable `aermod.x`.
  * `03-analysis/pipeline_scripts/` — Scripts en Python que construyen `.so`, `.emi` y `.inp`.
  * `03-analysis/run_aermod*/` — Directorios aislados por experimento para nunca sobrescribir corridas previas:
    * `run_aermod/` — Corrida base con emisión constante 24/7 (`PLOTFILE ANNUAL`).
    * `run_aermod_emisfact/` — Corrida con modulación horaria `MHRDOW` (`PLOTFILE ANNUAL`).
    * `run_aermod_postfile_95d/` — Corrida de alta resolución temporal con `POSTFILE` en ventana acotada (95 días).

## 2. Preprocesamiento Espacial y Meteorológico
* **Topografía y receptores (AERMAP):**
  * Proyección **UTM Zona 14N** (EPSG:32614).
  * **3,172 recintos escolares únicos (`RECID`)** (enlazados a 3,833 CCTs) procesados con DEM para calcular elevación base (Z_elev) y escala de colina (Z_hill), guardados en `receptores_elevados.rou`.
  * Altura de receptor fijada en `FLAGPOLE 1.5` (zona de respiración humana).
* **Meteorología de Capa Límite (AERMET):**
  * Estación **WMO 76679 (AICM)** para 2015–2019 (`PROFBASE 2230.0 METERS`).
  * Produce `aer_YYYY.sfc` (flujos turbulentos, u*, w*, Z_ic, Z_im, L, viento y temperatura) y `aer_YYYY.pfl` (perfiles verticales).

## 3. Inventario de Fuentes Fijas y Perfiles Temporales (`EMISFACT`)
* **Parametrización física (RETC -> AP-42):**
  * Filtrado a **285 fuentes fijas industriales activas** en la ZMVM (redujo el tiempo de cómputo de ~4 h a ~1.5 h por año).
  * Conversión a tasas de emisión de PM2.5 (g/s) y parámetros de chimenea (h_s, T_s, v_s, d_s) en 6 grupos (`SRCGROUP`): `TURBINA_`, `FUNDICIO`, `HORNO_VI`, `SECADO_Q`, `CALDERA_` y `ALL`.
* **Modulación temporal (`EMISFACT MHRDOW`):**
  * Matriz de **864 factores por fuente** (12 meses x 3 tipos de día [Lun–Vie, Sáb, Dom] x 24 horas) normalizados a media anual = 1.0 para garantizar conservación exacta de masa.
  * **5 perfiles industriales** (`CHEMICAL`: 115, `METALS`: 55, `PLAS_RUB`: 15, `FOODBEV`: 14, más `WATER`), anclados a calendario con inicio en miércoles (`2014-01-01`) tras verificar empíricamente la caída de actividad en fines de semana.
  * **2 perfiles eléctricos (CENACE, Sistema SIN - Área CEN, 2019–2021):** `CFE_BASE` (ciclo combinado proporcional a la demanda) y `CFE_PUNTA` (16 turbinas despachadas únicamente sobre el percentil 75%, 7,003.53 MWh, concentrando emisión en 157 celdas pico vespertino-nocturnas).
  * **69 fuentes constantes 24/7:** Hornos continuos (vidrio, cemento, celulosa) y establecimientos sin perfil específico.
* **Regla crítica de sintaxis en Fortran (`sources_emisfact_YYYY.so`):**
  * Orden obligatorio dentro del bloque `SO`: `LOCATION` -> `SRCPARAM` -> `EMISFACT` (máximo 6 columnas por línea) -> `SRCGROUP` al final. Invertir `EMISFACT` y `SRCGROUP` dispara el error fatal `SO E140`.

## 4. Ejecución de Corridas y Salidas (`PLOTFILE` vs. `POSTFILE`)
1. **Validación en seco (1 segundo):** Ejecutar `aermod.x` con `RUNORNOT NOT` antes de cada corrida masiva y confirmar `*** AERMOD Finishes Successfully ***` sin errores `E` en `.err`.
2. **Corridas anuales agregadas (`PLOTFILE ANNUAL`):**
   * Lanzadas vía script `.sh` para evitar errores de buffer o comillas en terminal.
   * **Rendimiento:** ~1 h 36 min por año en un núcleo (AERMOD es single-threaded); genera 30 archivos `.plt` de 335 KB (3,172 filas exactas) y sumarios `.sum` de 125 KB.
3. **Corridas de alta resolución temporal (`POSTFILE` — `run_aermod_postfile_95d/`):**
   * Vuelca la serie completa de concentraciones paso a paso (24 h o 1 h) por receptor y fecha. Permite construir exposición aguda, ventanas previas a evaluaciones o cortes por turno escolar.
   * **Reglas operativas:** El peso escala linealmente con R x H (receptores x horas/días) y puede llenar el disco rápido. En corridas largas es indispensable: (a) acotar fechas con `STARTEND` en el bloque `ME`, (b) usar `POLLUTID OTHER` cuando la ventana sea menor a 1 año (evita `MX E480` y `CO E363`), y (c) preferir promedio `24` o formato binario `UNFORM` si se requiere salida horaria (`1`).

## 5. Control de Calidad (Auditoría Rápida)
Una corrida se declara sana solo si cumple los 4 criterios:

    grep -E "AERMOD Finishes" aermod_*.out
    grep " E" errors_*.err | head -n 10
    ls -lh plot_*.plt summary_*.sum

1. Todos los `.out` cierran con `*** AERMOD Finishes Successfully ***`.
2. `errors_*.err` no contiene errores fatales (`RE W228` por usar `FLAGPOLE` global es esperado e inocuo).
3. El número de filas de cada `.plt` coincide con el total de receptores en `receptores_elevados.rou`.
4. Las concentraciones caen en rangos físicos coherentes (sin `NaN` ni ceros masivos).
