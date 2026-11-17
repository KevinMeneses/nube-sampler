#!/bin/zsh
# Abre la demo con el Rhodes ep_* en zonas (copia los samples a la biblioteca de pruebas), corre las pruebas de mouse de
# las zonas, cierra la demo y borra la copia. Uso: tests/ui_zones.sh   (mueve el mouse: no tocar la computadora)
cd "$(dirname "$0")/.."
LIB="$HOME/Library/Application Support/REAPER/Data/Nube Sampler/zz_pruebas/ep"
mkdir -p "$LIB" && cp "$HOME"/Music/ClaudeBeats/samples/ep_0*.wav "$LIB/"
NUBE_PRESET=0 NUBE_SAMPLE="zz_pruebas/ep/ep_048" NUBE_ZONES=1 tests/reopen.sh
python3 tests/ui_zones_test.py; r=$?
/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "$PWD/tests/ui_close.lua" >/dev/null 2>&1 &
sleep 3; rm -rf "$(dirname "$LIB")"
[ -n "$NUBE_KEEP_DEV" ] || source tests/fxname.sh limpiar
exit $r
