Guía de Compilación y Ejecución Nativa: AERMOD Suite en macOS (Apple Silicon ARM64)

Esta guía documenta los pasos técnicos para compilar y ejecutar de forma nativa la suite de modelación de dispersión atmosférica de la US EPA (AERMOD, AERMAP, AERMET y opcionalmente AERSURFACE) en procesadores Apple Silicon (M1/M2/M3/M4).

Este enfoque prescinde de emuladores x86 (Rosetta 2) y de máquinas virtuales Windows, aprovechando la velocidad de punto flotante del silicio de Apple mediante optimización -O3.

1. Prerrequisitos del Sistema

Se requiere el compilador de Fortran de GNU (gfortran). La vía recomendada en entornos Conda es:


conda install -c conda-forge fortran-compiler


Verificar la arquitectura de salida (debe responder arm64):


gfortran -dumpmachine


2. Fundamentos de Compilación en macOS

El código heredado de la EPA contiene inconsistencias de tipos y sintaxis que los compiladores modernos de GCC/Clang rechazan de manera estricta. Para lograr una compilación limpia, se deben respetar dos reglas:

1.     Banderas de relajación y optimización:
    ⚬         -O3: Vectorización y optimización matemática agresiva.
    ⚬         -w: Silencia advertencias no críticas.
    ⚬         -fno-range-check: Evita desbordamientos por enteros heredados de 16/32 bits.
    ⚬         -fallow-argument-mismatch: Permite discrepancias de tipos en llamadas a subrutinas Fortran heredadas.
2.     Separación de compilación y enlazado:
Compilar primero los módulos a código objeto (-c), compilar posteriormente el resto de las subrutinas y finalmente enlazar todos los archivos .o.

3. Procedimientos de Compilación

3.1. AERMOD (Motor de Dispersión)


# 1. Descarga y extracción
curl -O https://gaftp.epa.gov/Air/aqmg/SCRAM/models/dispersion/aermod/aermod_source.zip
unzip aermod_source.zip -d src_aermod
cd src_aermod/aermod_source_code_*

# 2. Permisos y limpieza
chmod -R u+w .
rm -f *.o *.mod aermod.x

# 3. Compilación de módulos
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch modules.f

# 4. Compilación de subrutinas (compatible con ZSH/Bash)
for f in *.f; do
  if [[ "$f" != "modules.f" ]]; then
    gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch "$f"
  fi
done

# 5. Enlazado final
gfortran -O3 -w -o aermod.x *.o
chmod +x aermod.x
mv aermod.x ../../aermod_bin/
cd ../..


3.2. AERMAP (Procesador de Terreno)

    Parche Obligatorio en el Código Fuente:
En la línea 118 de sub_recelv.f, el código original de la EPA omite una coma en un descriptor de formato de salida, lo que detiene la ejecución durante el procesamiento de receptores (Fortran runtime error: Missing comma between descriptors).


# 1. Descarga y extracción
curl -O https://gaftp.epa.gov/Air/aqmg/SCRAM/models/related/aermap/aermap_source.zip
unzip aermap_source.zip -d src_aermap
cd src_aermap/aermap_source_code_*

# 2. Permisos y limpieza
chmod -R u+w .
rm -f *.o *.mod aermap.x

# 3. Aplicar corrección en sub_recelv.f
# Línea original:  (/A3,' FILE NAD:  ',I3' ;  ANCHOR POINT NAD: ',I3/)
# Línea corregida: (/A3,' FILE NAD:  ',I3,' ;  ANCHOR POINT NAD: ',I3/)
sed -i '' "s/I3' ;  ANCHOR POINT NAD:/I3,' ;  ANCHOR POINT NAD:/g" sub_recelv.f

# 4. Compilación de módulos
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_*.f

# 5. Compilación del resto del código
for f in *.f; do
  if [[ "$f" != mod_* ]]; then
    gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch "$f"
  fi
done

# 6. Enlazado final
gfortran -O3 -w -o aermap.x *.o
chmod +x aermap.x
mv aermap.x ../../aermod_bin/
cd ../..


3.3. AERMET (Procesador Meteorológico)

AERMET está programado en Fortran 90 (.f90) y exige una resolución jerárquica estricta de sus módulos para evitar errores de símbolos no definidos.


# 1. Descarga y extracción
curl -O https://gaftp.epa.gov/Air/aqmg/SCRAM/models/met/aermet/aermet_source.zip
unzip aermet_source.zip -d src_aermet
cd src_aermet

# 2. Permisos y limpieza
chmod -R u+w .
rm -f *.o *.mod aermet.x

# 3. Módulos base independientes
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_file_units.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_main1.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_surface.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_upperair.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_onsite.f90

# 4. Módulos dependientes
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_pbl.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_misc.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_read_input.f90
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_reports.f90

# 5. Programa principal
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch aermet.f90

# 6. Enlazado final
gfortran -O3 -w -o aermet.x *.o
chmod +x aermet.x
mv aermet.x ../../aermod_bin/
cd ../..


3.4. AERSURFACE (Opcional - Uso de Suelo NLCD)

    Nota para México / CDMX: AERSURFACE procesa exclusivamente bases de datos NLCD de EE. UU. Para cuencas mexicanas, los parámetros superficiales (albedo, relación de Bowen y rugosidad superficial $z_0$) se derivan de INEGI y se declaran directamente en aermet.inp mediante SITE_CHAR.


# 1. Descarga y extracción
curl -O https://gaftp.epa.gov/Air/aqmg/SCRAM/models/related/aersurface/aersurface_source.zip
unzip aersurface_source.zip -d src_aersurface
cd src_aersurface

# 2. Permisos y limpieza
chmod -R u+w .
rm -f *.o *.mod aersurface.x

# 3. Compilar módulos
gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch mod_*.f

# 4. Compilar subrutinas
for f in *.f; do
  if [[ "$f" != mod_* ]]; then
    gfortran -c -O3 -w -fno-range-check -fallow-argument-mismatch "$f"
  fi
done

# 5. Enlazado final
gfortran -O3 -w -o aersurface.x *.o
chmod +x aersurface.x
mv aersurface.x ../../aermod_bin/
cd ../..


4. Consideraciones Críticas de Ejecución

4.1. Sintaxis de Rutas (Windows vs. Unix)

Los archivos de control (.inp) elaborados en Windows suelen contener rutas relativas con diagonales invertidas (..\AERMET\Parish2020.SFC). En macOS/Linux deben sustituirse estrictamente por diagonales normales:


ME STARTING
   SURFFILE  ../AERMET/Parish2020.SFC
   PROFFILE  ../AERMET/Parish2020.PFL


4.2. Declaración de LOCATION en AERMET

La sintaxis de la tarjeta LOCATION requiere un orden estricto de parámetros posicionales:


LOCATION [STATION_ID] [LATITUD] [LONGITUD] [TIME_ZONE_ADJ] [ELEVATION]


Si se omite el huso horario, el compilador interpretará la elevación como el ajuste horario, arrojando el error:
EXCEEDS 12 HOUR ADJUSTMENT FOR TIME ZONE ADJUSTMENT.
Ejemplo para huso horario Centro (CST = 6) y elevación de 29 m:


LOCATION 12960 29.97N 95.35W 6 29


4.3. Diagnóstico en ERRORS.OUT

AERMOD clasifica sus salidas por severidad en la primera columna:

⚬     E (Fatal Error): Interrumpe la simulación.
⚬     W (Warning): Advertencia regulatoria o de consistencia (e.g., W530 por discrepancia de ID de estación). No detiene el cómputo.
⚬     I (Informational): Eventos operacionales de rutina (e.g., I440 para horas de viento en calma y I460 para horas sin registro).

Una corrida es exitosa si el bloque final de aermod.out concluye con:


************************************
*** AERMOD Finishes Successfully ***
************************************



---

## Bitácora de avances — Noviembre 2026 (Cierre de tesis Cap. 3–4 y POSTFILE 95d)

### 2026-11-05 a 2026-11-18 — Panel PLANEA–AERMOD, TWFE y focalización
* Consolidación del panel en la Cuenca de México (2015, 2017 y 2019): **2,392 recintos escolares** (2,964 CCT, 9,459 observaciones) cruzados con 285 fuentes fijas activas del RETC parametrizadas con factores AP-42 y perfiles horarios `EMISFACT MHRDOW`.
* **TWFE anual:** efecto promedio metropolitano indistinguible de cero; en secundarias públicas de alta marginación se identifica una interacción significativa en Lenguaje y Comunicación (-98.30 puntos, p = 0.023; efecto total de -95.76 puntos por ug/m3, p = 0.025), equivalente a **-13.4 puntos** por la brecha entre quintiles extremos (0.14 ug/m3), estable en cinco especificaciones de robustez.
* **Focalización de política pública:** identificación de **27 recintos escolares prioritarios** (36 CCT, ~17,600 estudiantes; inversión inicial estimada en filtración HEPA de $2.46M MXN) y **56 establecimientos** (47 fundiciones y 9 vidrieras) que concentran el 40.58% de las emisiones.

### 2026-11-19 a 2026-11-21 — Corridas horarias AERMOD (`POSTFILE 95d`) y 2SLS físico
* Conclusión de las simulaciones horarias (`AVERTIME 1`, `POSTFILE`) para la ventana de 95 días alrededor de PLANEA (28 abr – 31 jul de 2015, 2017 y 2019), filtradas al horario lectivo exacto de cada turno escolar.
* **Estrategia IV (30 días previos, horario de turno, instrumentada con dirección del viento y emisiones fijas de 2015):** en secundarias públicas de alta marginación, forma reducida de **-10.70 puntos por DE** (p = 0.027) y estimador 2SLS físico de **-450.38 puntos por ug/m3** (p = 0.006; IC Anderson-Rubin 95% [-932.4, -80.7]).
* Empaquetado del kit de onboarding y runbook reproducible en `00-onboarding-aermod/` para continuidad del laboratorio.
