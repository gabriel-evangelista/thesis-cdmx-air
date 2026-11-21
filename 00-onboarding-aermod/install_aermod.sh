#!/bin/zsh
set -e

echo "=== 1. Verificando compilador gfortran ==="
if ! command -v gfortran &> /dev/null; then
    echo "Error: gfortran no encontrado."
    echo "  - macOS (Homebrew): brew install gcc"
    echo "  - Ubuntu / Debian : sudo apt install gfortran"
    exit 1
fi
gfortran --version | head -n 1

SRC_DIR="./aermod_source"
BIN_DIR="../03-analysis/aermod_bin"
mkdir -p "$BIN_DIR"

if [ ! -d "$SRC_DIR" ]; then
    echo "Descarga el código fuente oficial (aermod_source.zip, v24142 o superior) desde:"
    echo "https://www.epa.gov/scram/air-quality-dispersion-modeling-preferred-and-recommended-models#aermod"
    echo "Descomprímelo en $SRC_DIR y vuelve a ejecutar este script."
    exit 1
fi

echo "=== 2. Compilando módulos y ejecutable aermod.x ==="
cd "$SRC_DIR"

# Banderas críticas para gfortran moderno (Apple Silicon / Linux GCC 10+)
FLAGS="-O2 -fno-range-check -fallow-argument-mismatch"

# Compilación ordenada: módulos primero, luego rutinas principales
for f in modules.f grsm.f aermod.f setup.f coset.f soset.f reset.f meset.f ouset.f \
         inpsum.f metext.f iblval.f siggrid.f tempgrid.f windgrid.f calc1.f calc2.f \
         prise.f prime.f sigmas.f pitarea.f uninam.f output.f evset.f evcalc.f evoutput.f \
         rline.f bldown.f; do
    if [ -f "$f" ]; then
        echo "  Compilando $f ..."
        gfortran -c $FLAGS "$f"
    fi
done

echo "=== 3. Enlazando binario final ==="
gfortran -o "$BIN_DIR/aermod.x" $FLAGS *.o
rm -f *.o *.mod

echo "[OK] Binario compilado en: $BIN_DIR/aermod.x"
echo "Nota: Para AERMAP y AERMET el flujo es idéntico usando las mismas banderas ($FLAGS)."
