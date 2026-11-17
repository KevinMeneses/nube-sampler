#!/bin/zsh
# Cierra la demo de la interfaz (si hay) y la vuelve a abrir con el código nuevo.
# NUBE_PRESET=n NUBE_SAMPLE="Nube/..." eligen preset y sample; NUBE_SHOT=archivo.png toma captura.
cd "$(dirname "$0")"
R=/Applications/REAPER.app/Contents/MacOS/REAPER
mkdir -p out
python3 ../tools/build.py >/dev/null || exit 1
osascript -e 'tell application "System Events" to tell process "REAPER" to get name of every window' 2>/dev/null | grep -q "Nube Sampler demo" && { $R -nonewinst "$PWD/ui_close.lua" >/dev/null 2>&1 & sleep 3; }
echo "${NUBE_PRESET:-7} ${NUBE_SAMPLE:-Nube/Loop - Chill 90 BPM 4 compases}" > out/demo_opts.txt; rm -f out/ui.txt
$R -nonewinst "$PWD/ui_demo.lua" >/dev/null 2>&1 &
for i in $(seq 1 20); do grep -q done out/ui.txt 2>/dev/null && break; sleep 0.5; done; sleep 2.5
[ -n "$NUBE_SHOT" ] && python3 -c "import sys; sys.path.insert(0, '.'); from ui import shot; shot('$NUBE_SHOT')"
echo listo
