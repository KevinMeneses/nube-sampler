#!/bin/zsh
# Renderiza los casos en REAPER (pestaña temporal) y verifica contra la teoría. Uso: tests/run.sh [patrones de casos...]
cd "$(dirname "$0")/.."
PY=${NUBE_PY:-python3}   # necesita numpy, scipy y soundfile
python3 tools/build.py >/dev/null || exit 1
python3 tools/check_order.py || exit 1
python3 tools/check_names.py || exit 1
source tests/fxname.sh
[ -f tests/samples/pcm16.wav ] || $PY tests/make_signals.py || exit 1
LIB="$HOME/Library/Application Support/REAPER/Data/Nube Sampler/zz_pruebas"
mkdir -p "$LIB" && cp -R tests/samples/. "$LIB/"
mkdir -p tests/out; echo "$*" > tests/out/only.txt
rm -f tests/out/log.txt
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/render_cases.lua" >/dev/null 2>&1 &
for i in $(seq 1 600); do grep -q done tests/out/log.txt 2>/dev/null && break; sleep 1; done
grep -q done tests/out/log.txt || { echo "REAPER no terminó (¿diálogo abierto?)"; exit 1; }
grep -i error tests/out/log.txt
rm -rf "$LIB"   # que las señales de prueba no queden en la biblioteca del usuario
[ -n "$NUBE_KEEP_DEV" ] || source tests/fxname.sh limpiar
[ -n "$1" ] && exit 0
$PY tests/check.py
