# Diccionario de Insumos para Replicar AERMOD en México

Todos los insumos espaciales (fuentes y receptores) deben proyectarse a coordenadas planas **UTM** correspondientes a la zona metropolitana de estudio (ej. **UTM 14N / EPSG:32614** para CDMX y Monterrey; **UTM 13N / EPSG:32613** para Guadalajara).

| Insumo | Fuente Oficial | Formato de Entrada | Qué se extrae y cómo se usa |
| :--- | :--- | :--- | :--- |
| **1. Topografía (DEM)** | INEGI (Continuo de Elevaciones Mexicano, CEM 3.0) o NASA SRTM (30 m) | GeoTIFF (`.tif`) | Insumo de **AERMAP** para calcular elevación base ($Z_{\text{elev}}$) y escala de colina ($Z_{\text{hill}}$) de cada receptor y chimenea. |
| **2. Meteorología de Superficie** | NOAA Integrated Surface Database (ISD) o redes locales (SIMAT/RAMA, SIMA) | ISHD / ASCII horario | Temperatura, dirección y velocidad de viento, nubosidad y presión en aeropuerto principal (ej. WMO `76679` AICM para CDMX). Entra a **AERMET Etapa 1**. |
| **3. Radiosondeo (Perfil Vertical)** | Universidad de Wyoming (vía librería Python `siphon`) o NOAA NCEI IGRA v2 | FSL / IGRA (00Z y 12Z) | Perfil vertical de temperatura y viento para calcular altura de capa de mezcla ($Z_{ic}, Z_{im}$) en **AERMET**. |
| **4. Inventario de Fuentes Fijas** | SEMARNAT — RETC (Registro de Emisiones y Transferencia de Contaminantes) o COA estatal | CSV / Excel | Coordenadas, sector/SCIAN y emisiones anuales (ton/año -> g/s). Cuando no se reportan partículas o parámetros de chimenea ($h_s, T_s, v_s, d_s$), se aplican razones y perfiles estándar **US EPA AP-42** por rama tecnológica. |
| **5. Perfiles Temporales (`EMISFACT`)** | CENACE (Mercado del Día en Adelanto, `SIN`) + curvas sectoriales de carga | CSV horario (8,760 h) | Se convierten a matriz **`MHRDOW`** (864 factores con media = 1.0) para conservar la masa anual emitida y acoplar el despacho vespertino/nocturno con la inversión térmica. |

## Checklist mínimo al cambiar de ciudad
1. Actualizar el código EPSG de la zona UTM en los scripts de proyección (`pyproj`).
2. Cambiar `SURFDATA`, `UAIRDATA` y `PROFBASE` (altitud en metros sobre el nivel del mar de la estación meteorológica) en el bloque `ME` de `aermod.inp`.
3. Verificar que el calendario de las curvas `EMISFACT` coincida con el día de la semana real (caída en sábado y domingo) antes de generar los archivos `.so`.
4. Correr una validación en seco con `RUNORNOT NOT` (1 segundo) antes de lanzar cualquier corrida anual o `POSTFILE`.
