# Glosario de Errores Comunes en AERMOD (Laboratorio)

| Síntoma / Código | Causa real | Solución |
| :--- | :--- | :--- |
| **`SO E140`** (`Invalid Order of Keyword: SRCGROUP`) | Se colocaron tarjetas `EMISFACT` después de `SRCGROUP` en el archivo `.so`. | Reordenar el archivo `.so` para que `SRCGROUP` sea siempre la última sección antes de `SO FINISHED`. |
| **`SO E206`** (`Source ID Not Found`) | El tercer campo de `EMISFACT` usa un nombre de grupo (ej. `CHEMICAL`) en vez del `SRCID` exacto. | Escribir `EMISFACT` usando el `SRCID` individual definido en `LOCATION` (máx. 12 caracteres). |
| **`CO E363`** (`Multiyr 24h/Ann PM25 processing not applicable`) | Con `MODELOPT DFAULT` + `POLLUTID PM25`, la regla regulatoria EPA prohíbe `AVERTIME 1` o `PERIOD`. | Cambiar `POLLUTID PM25` por `POLLUTID OTHER` (la física de dispersión es idéntica y habilita 1h y `PERIOD`). |
| **`MX E480`** (`Less than 1yr for MULTYEAR... PM25AVE`) | Con `POLLUTID PM25` y menos de 1 año calendario de meteorología (ej. ventanas cortas o pruebas), falla en la fase de salida. | Cambiar `POLLUTID PM25` por `POLLUTID OTHER` para corridas subanuales. |
| **Error de lectura en `EMISFACT` / números truncados** | Más de 8–12 factores por línea superan el límite de ancho de columna en Fortran (~132 caracteres). | Formatear `EMISFACT` en **6 factores por línea** (144 líneas por fuente para `MHRDOW`). |
| **`RE W228`** (cientos de warnings `DISCCART`) | Se usa el `FLAGPOLE 1.5` global en `CO` sin repetir `1.5` en cada línea `DISCCART`. | **No es un error.** Ignorarlo; verificar únicamente que `grep " E" errors_*.err` salga vacío. |
| **Fallo el 31 de diciembre en año bisiesto (ej. 2016)** | Un archivo horario fijo (`HOUREMIS`) de 8,760 horas no cubre las 8,784 horas de un año bisiesto. | Usar `EMISFACT MHRDOW` (864 factores independientes de si el año tiene 365 o 366 días). |
| **Terminal congelada mostrando `dquote>`** | Al pegar un bucle largo en `zsh`, quedó una comilla abierta o un espacio invisible (`NBSP`). | Presionar `Ctrl + C`, guardar el bucle en un archivo `.sh` ejecutable (`chmod +x`) y correrlo directo. |
| **Disco lleno al usar `POSTFILE`** | `POSTFILE` en texto (`PLOT`) guarda $R \times H$ filas (ej. 3,172 receptores $\times$ 8,760 h $\approx 27.8\text{M}$ de líneas/año). | Acotar días con `STARTEND` en el bloque `ME`, usar promedio `24` en vez de `1`, o exportar en binario (`UNFORM`). |
