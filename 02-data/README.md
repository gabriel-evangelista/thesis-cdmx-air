# Acceso a Datos Crudos y Procesados (`02-data/`)

Por tamaño (mosaicos GeoTIFF SRTM, salidas horarias de AERMOD y archivos `.parquet`), los archivos de datos están excluidos de Git y aquí solo se conserva la estructura de carpetas mediante `.gitkeep`.

## Cómo obtener los datos

Los insumos crudos (`raw/`) y procesados (`processed/`) completos están alojados en Google Drive con acceso controlado:

* **Carpeta de datos en Google Drive:** [Solicitar acceso a `02-data/`](https://drive.google.com/drive/folders/1vlM3Sk6fUn42-wXuBqnESfhTjzOz6t1I?usp=sharing)

Al abrir el enlace, haz clic en **Solicitar acceso** indicando brevemente tu afiliación o uso previsto (replicación, proyecto del laboratorio, etc.) y se te concederá permiso de lectura.

## Qué incluye la carpeta

* **`raw/`**: Inventarios RETC (2015–2019), bases PLANEA y catálogo SIGED, meteorología de superficie (NOAA ISD), radiosondeos (IGRA), pronósticos horarios CENACE y curvas de carga industrial.
* **`processed/`**: Salidas de `AERMAP` (`receptores_elevados.rou`, `sources_*.so`), meteorología procesada de `AERMET` (`.sfc`, `.pfl`), factores horarios `EMISFACT MHRDOW`, mosaicos DEM y paneles listos para econometría.

> **Nota:** Si solo quieres probar que tu instalación local de AERMOD funciona antes de descargar los datos completos, usa el caso de prueba autocontenido (~256 KB) en [`../00-onboarding-aermod/toy_case/`](../00-onboarding-aermod/toy_case/).
