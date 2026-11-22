# Kit de Onboarding y Runbook Operativo: AERMOD (Laboratorio)

Flujo reproducible de código abierto para modelar dispersión atmosférica hiperlocal de PM2.5 (a 1.5 m de altura) desde fuentes fijas industriales en macOS (Apple Silicon / Intel) y Linux, sin licencias comerciales.

## Contenido de esta carpeta
* `RUNBOOK.md` — Runbook operativo completo del pipeline AERMOD (EMISFACT MHRDOW, POSTFILE y control de calidad).
* `install_aermod.sh` — Script de compilación nativa de AERMOD `v24142` con `gfortran`.
* `environment.yml` — Entorno Conda (`aermod-lab`) para preprocesamiento, GIS y econometría (`pyfixest`).
* `toy_case/` — Caso de prueba autocontenido (5 fuentes, 20 receptores, 7 días) que corre en ~2 segundos.
* `TEMPLATE_aermod.inp` — Plantilla maestra comentada indicando qué parámetros se editan y cuáles quedan fijos.
* `TROUBLESHOOTING.md` — Glosario de errores comunes en Fortran/AERMOD (`SO E140`, `CO E363`, `MX E480`, `RE W228`, etc.).
* `DATA_DICTIONARY.md` — Fuentes oficiales y formatos para replicar el pipeline en otras ciudades de México.

---

## Inicio Rápido (5 minutos)

1. **Crear entorno Python:**

        conda env create -f environment.yml
        conda activate aermod-lab

2. **Compilar el binario `aermod.x`:**
   Descarga `aermod_source.zip` desde EPA SCRAM, descomprímelo en `00-onboarding-aermod/aermod_source/` y ejecuta:

        ./install_aermod.sh

3. **Validar la instalación con el Toy Case:**

        cd toy_case
        ../../03-analysis/aermod_bin/aermod.x
        tail -n 5 aermod.out

   Debes ver `*** AERMOD Finishes Successfully ***` y archivos no vacíos en `toy_plot_24h.plt` y `toy_post_24h.pst`.

---

## Runbook Técnico del Pipeline (Referencia ZMVM 2015–2019)

### 1. Preprocesamiento Espacial y Meteorológico
* **Topografía (`AERMAP`):** Proyección UTM 14N. Se procesaron **3,172 recintos escolares únicos (`RECID`)** para obtener Z_elev y Z_hill (`receptores_elevados.rou`), con altura de respiración `FLAGPOLE 1.5`.
* **Meteorología (`AERMET`):** Estación WMO `76679` (AICM, `PROFBASE 2230.0 METERS`), generando `aer_YYYY.sfc` y `aer_YYYY.pfl`.

### 2. Fuentes Fijas y Modulación Temporal (`EMISFACT MHRDOW`)
* **Inventario (`RETC` -> `AP-42`):** 285 fuentes fijas industriales activas agrupadas en 6 ramas tecnológicas (`SRCGROUP`).
* **Perfiles temporales (`MHRDOW`):** Matriz de **864 factores por fuente** (12 meses x 3 tipos de día x 24 horas) con media anual = 1.0, combinando 5 curvas industriales (ancladas al ciclo semanal real) y 2 curvas de despacho eléctrico del CENACE (`CFE_BASE` y `CFE_PUNTA` sobre el percentil 75%).
* **Regla de sintaxis en `.so`:** Orden estricto `LOCATION` -> `SRCPARAM` -> `EMISFACT` (máx. 6 columnas/línea) -> `SRCGROUP` al final.

### 3. Ejecución: `PLOTFILE` vs. `POSTFILE`
* **Aislamiento:** Cada experimento corre en su propia carpeta (`run_aermod/`, `run_aermod_emisfact/`, `run_aermod_postfile_95d/`).
* **Corridas anuales (`PLOTFILE ANNUAL`):** ~1.5 h por año en un núcleo; genera archivos `.plt` ligeros (~335 KB para 3,172 receptores). Ejecutar siempre vía script `.sh`.
* **Corridas de alta resolución (`POSTFILE`):** Exporta concentraciones paso a paso (24 h o 1 h) por receptor y fecha (usado en ventanas acotadas como `run_aermod_postfile_95d/`). **Regla operativa:** como el tamaño crece con R x H, acotar fechas con `STARTEND` en el bloque `ME`, usar promedio `24` o formato binario (`UNFORM`) para salidas horarias, y cambiar `POLLUTID PM25` a `OTHER` en ventanas menores a 1 año.

### 4. Control de Calidad (Checklist de Salidas Sanas)
1. `grep "AERMOD Finishes" aermod_*.out` muestra `Successfully` en todos los años.
2. `grep " E" errors_*.err` no devuelve errores fatales (`RE W228` es esperado e inocuo).
3. El número de filas en cada `.plt` coincide exactamente con los receptores en `.rou`.
4. Los valores de concentración están en rangos físicos coherentes (sin `NaN` ni ceros masivos).
