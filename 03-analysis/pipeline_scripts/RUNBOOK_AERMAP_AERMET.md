# Bitácora Técnica de Replicabilidad: Pipeline AERMET -> AERMAP -> AERMOD

Este documento registra las reglas técnicas, decisiones metodológicas y correcciones de sintaxis en Fortran descubiertas durante la construcción del modelo para la ZMVM (2015-2019).

---

## 1. Preprocesamiento de Escuelas (PLANEA + SIGED)
* **Panel Balanceado:** Se exigen escuelas presentes en los tres cortes (2015, 2017, 2019).
* **Turnos vs. Inmuebles Físicos:** Cada clave `CCT` en México representa un centro de trabajo/turno, no necesariamente un edificio distinto.
  * *Regla:* Para AERMAP y AERMOD se colapsan las coordenadas `(X_UTM, Y_UTM)` mediante `drop_duplicates()` para modelar únicamente **inmuebles físicos únicos** (3,172 en ZMVM).
  * *Enlace Econométrico:* Se mantiene el archivo `tabla_enlace_cct_recid.csv` que vincula las 3,833 CCTs evaluadas con su `RECID` (`R00001` a `R03172`).
* **Corrupción de caracteres en SIGED:** El catálogo original de SEP contiene sustituciones Unicode atípicas (`ɠ` -> `É`, `ӎ` -> `ÓN`). No afectan a AERMAP/AERMOD ni al cruce por `CCT`, pero se limpian por diccionario para tablas descriptivas.

---

## 2. Reglas Críticas para AERMAP (v24142) con GeoTIFF SRTM 30m

### A. Sintaxis estricta del bloque CO
1. **`DATATYPE NED`**: Nunca agregar la palabra `TIFF` en el renglón `DATATYPE` (el segundo parámetro opcional es `FILLGAPS`).
2. **`DATAFILE nombre.tif`**: Nunca agregar la palabra `TIFF` al final del renglón `DATAFILE` (el parámetro opcional es `CHECK` y causa Error `CO E203`).
3. **`DOMAINXY` sobre `DOMAINLL`**: Cuando el dominio cruza el meridiano central o bordes en longitudes negativas (Oeste), `DOMAINLL` puede detonar `CO E242: Anchor UTM zone is out of range`. Usar siempre `DOMAINXY` expresado en metros UTM con el número de zona positivo (`14`).
4. **Efecto de curvatura UTM en `CHKEXT` (`OU E300` / `OU E305`)**:
   * AERMAP convierte las esquinas Suroeste y Noreste de `DOMAINXY` a Lat/Lon y verifica que ningún receptor/fuente rebase ni la caja UTM ni la caja Lat/Lon resultante.
   * Debido a la convergencia de meridianos cerca del meridiano central (-99.0W), un punto con `Y_UTM` menor al borde superior puede tener una latitud ligeramente mayor que la esquina Noreste.
   * *Solución:* Filtrar siempre fuentes y receptores aplicando tanto el recorte en metros UTM como el recorte en las latitudes/longitudes exactas de las esquinas de `DOMAINXY`.

### B. Sintaxis estricta de Bloques SO y RE en AERMAP
* **Fuentes (`SO`):** `LOCATION <SRCID> POINT <X_UTM> <Y_UTM>` (acepta `SRCID` de hasta 12 caracteres).
* **Receptores (`RE`):** `DISCCART <X_UTM> <Y_UTM>` (exclusivamente 2 números en la entrada de AERMAP; si se incluyen los `0.0 0.0` de elevación que usa AERMOD, AERMAP falla).

---

## 3. Reglas para AERMET (2015-2019)
* **Estación Base:** AICM (`19.436N 99.072W`, `UA_ID: 76679`, `SF_ID: 766793`).
* **Verificación de integridad:**
  * Años normales (2015, 2017, 2018, 2019): `.pfl` = 8,760 líneas | `.sfc` = 8,761 líneas (incluye 1 línea de header).
  * Años bisiestos (2016): `.pfl` = 8,784 líneas | `.sfc` = 8,785 líneas.
* **Ubicación consolidada:** `02-data/processed/aermet_out/`.

---

## 4. Parámetros de Exposición en AERMOD
* **Zona de respiración humana (`FLAGPOLE`):** Se utiliza `FLAGPOLE 1.5` en el bloque `CO` de AERMOD (estándar US EPA HHRAP para altura media de inhalación en adolescentes/alumnos de secundaria), utilizando directamente `receptores_elevados.rou` y `fuentes_elevadas.sou` desde `02-data/processed/aermap_out/`.

---

## 5. Control de Versiones y Checkpoints de Pipeline
* **Tag:** `v1.0-aermap-aermet-ready`
* **Estado validado:**
  * Meteorología ZMVM 2015-2019 lista y verificada en `02-data/processed/aermet_out/`.
  * Elevaciones de fuentes (`fuentes_elevadas.sou`, N=716) y receptores escolares (`receptores_elevados.rou`, N=3,172) calculadas con SRTM 30m en `02-data/processed/aermap_out/`.
  * Catálogo de escuelas sincronizado (`tabla_enlace_cct_recid.csv`, N=3,833 turnos/CCT vinculados a los 3,172 inmuebles físicos).
  * Exclusiones en `.gitignore` estabilizadas (eliminación de datos binarios y directorios de tutoriales pesados).

---

## 6. Parametrización Tecnológica de Fuentes Fijas RETC (AP-42 -> AERMOD SO)
* **Script generador:** `03-analysis/pipeline_scripts/build_aermod_sources.py`
* **Universo activo:** De las 716 instalaciones ubicadas en el dominio ZMVM, **285 plantas** reportan emisiones positivas de $\text{CO}_2$ (`CAS 124-38-9`). Se filtraron las 431 plantas vacías para optimizar el tiempo de cómputo de AERMOD en $2.51\times$ sin alterar las elevaciones `Z_ELEV` calculadas por AERMAP.
* **Limpieza de outliers:** Corrección manual en `retc_15_19_pm_est_complete_clean.csv` del salto decimal ($10\times$) en `ICA7P0901111` (2017) y remoción de eventos atípicos de comisionamiento/regularización en 2016 (`TPN0901600351`, `RMCMB1512111`).
* **Matriz de asignación tecnológica y termodinámica (285 fuentes):**
  * `CALDERA_IND` (Default/Baseline AP-42 Sec. 1.4 - Papel, Alimentos, Farmacéutica, Automotriz): **191 plantas** | Ratio = `0.0633 kg PM/t CO2` | $h_s=15\text{m}, T_s=450\text{K}, v_s=10\text{m/s}, d_s=0.80\text{m}$.
  * `FUNDICION_METAL` (AP-42 Sec. 12.8/12.9 controlado con filtros de mangas): **47 plantas** | Ratio = `0.6500 kg PM/t CO2` | $h_s=22\text{m}, T_s=370\text{K}, v_s=12\text{m/s}, d_s=1.10\text{m}$.
  * `SECADO_QUIM` (AP-42 Sec. 8.20 - Detergentes, polvos químicos, pinturas): **19 plantas** | Ratio = `0.2500 kg PM/t CO2` | $h_s=25\text{m}, T_s=365\text{K}, v_s=11\text{m/s}, d_s=1.20\text{m}$.
  * `TURBINA_GAS` (AP-42 Sec. 3.1 - CFE CTGs, Cogeneración, Compresión): **17 plantas** | Ratio = `0.0600 kg PM/t CO2` | $h_s=30\text{m}, T_s=750\text{K}, v_s=28\text{m/s}, d_s=3.20\text{m}$.
  * `HORNO_VIDRIO` (AP-42 Sec. 11.15 controlado - Vidrio y minerales no metálicos): **9 plantas** | Ratio = `0.4500 kg PM/t CO2` | $h_s=45\text{m}, T_s=550\text{K}, v_s=15\text{m/s}, d_s=1.80\text{m}$.
  * `MOTOR_RICE` (AP-42 Sec. 3.2 - Motores estacionarios combustión interna): **2 plantas** | Ratio = `0.1300 kg PM/t CO2` | $h_s=12\text{m}, T_s=673\text{K}, v_s=22\text{m/s}, d_s=0.45\text{m}$.
* **Outputs generados en `02-data/processed/aermap_out/`:**
  * `catalogo_285_fuentes_aermod_ap42.csv`
  * `fuentes_285_filtradas.sou`
  * `sources_2015.so` a `sources_2019.so` (con bloques `LOCATION`, `SRCPARAM` y `SRCGROUP` por rama tecnológica y `ALL`).

---

## 7. Ensamblaje y Validación de Sintaxis de AERMOD (Commit 2)
* **Script generador de control:** `03-analysis/pipeline_scripts/build_aermod_inp.py`
* **Archivos `.inp` generados:** `aermod_2015.inp` al `aermod_2019.inp` ubicados en `03-analysis/run_aermod/`.
* **Estructura de control validada:**
  * Bloque `CO`: `FLAGPOLE 1.5` (zona de respiración humana de 1.5 m sobre el terreno) y validación de sintaxis con `RUNORNOT`.
  * Bloque `SO`: Inclusión dinámica de los archivos anuales `sources_YYYY.so` (N=285 fuentes con elevación y parámetros AP-42).
  * Bloque `RE`: Inclusión de `receptores_elevados.rou` (N=3,172 inmuebles escolares).
  * Bloque `ME`: Datos meteorológicos superficiales y de perfil de la estación AICM (`76679`) procesados por AERMET (2015–2019).
* **Resultado de ejecución de prueba:** `*** AERMOD Finishes Successfully ***` con los binarios nativos de macOS (`aermod.x`).
