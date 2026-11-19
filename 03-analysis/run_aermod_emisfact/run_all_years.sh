#!/bin/zsh
set -e

cd /Users/gabrielevangelista/thesis-cdmx-air/03-analysis/run_aermod_emisfact
AERMOD_BIN="/Users/gabrielevangelista/thesis-cdmx-air/03-analysis/aermod_bin/aermod.x"

for yr in 2015 2016 2017 2018 2019; do
    echo "===================================================="
    echo "Iniciando corrida de AERMOD + EMISFACT para el año $yr ..."
    echo "===================================================="

    sed 's/RUNORNOT  NOT/RUNORNOT  RUN/g' aermod_${yr}.inp > aermod.inp

    time "$AERMOD_BIN"

    mv aermod.out aermod_emi_${yr}.out

    echo "[OK] Finalizado y respaldado año $yr con EMISFACT."
    echo ""
done

echo "¡Todas las corridas nocturnas con EMISFACT han concluido con éxito!"
