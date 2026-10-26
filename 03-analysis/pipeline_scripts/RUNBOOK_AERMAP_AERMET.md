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
