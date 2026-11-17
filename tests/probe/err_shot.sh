#!/bin/zsh
# Captura la ventana del FX recién insertado (errores de compilación incluidos) en tests/out/err.png.
cd "$(dirname "$0")/../.."
source tests/fxname.sh
R=/Applications/REAPER.app/Contents/MacOS/REAPER
rm -f tests/out/err.txt tests/out/err.png
$R -nonewinst "$PWD/tests/probe/err_open.lua" >/dev/null 2>&1 &
for i in $(seq 1 30); do grep -q done tests/out/err.txt 2>/dev/null && break; sleep 0.5; done; sleep 2
WID=$(swift tests/winid.swift "Nube Sampler"); echo "ventana $WID"
[ -n "$WID" ] && screencapture -x -o -l$WID tests/out/err.png
$R -nonewinst "$PWD/tests/probe/err_close.lua" >/dev/null 2>&1 &
for i in $(seq 1 30); do grep -q closed tests/out/err.txt 2>/dev/null && break; sleep 0.5; done; cat tests/out/err.txt
