#!/bin/zsh
# Rhodes de "Nube baja": 17 RS5k (pista 10 del experimento) contra Nube Sampler con zonas. Uso: tests/rs5k/run.sh
cd "$(dirname "$0")/../.."
PY=${NUBE_PY:-python3}
python3 tools/build.py >/dev/null || exit 1
python3 tools/check_order.py || exit 1
source tests/fxname.sh
LIB="$HOME/Library/Application Support/REAPER/Data/Nube Sampler/zz_pruebas/ep"
mkdir -p "$LIB" && cp "$HOME"/Music/ClaudeBeats/samples/ep_0*.wav "$LIB/"
rm -f tests/out/rs5k_log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/rs5k/compare.lua" >/dev/null 2>&1 &
for i in $(seq 1 600); do grep -q done tests/out/rs5k_log.txt 2>/dev/null && break; sleep 1; done
cat tests/out/rs5k_log.txt
rm -rf "$(dirname "$LIB")"
[ -n "$NUBE_KEEP_DEV" ] || source tests/fxname.sh limpiar
grep -q done tests/out/rs5k_log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
$PY tests/rs5k/check.py
