#!/bin/zsh
# Instala Nube Sampler en REAPER (macOS) como enlaces: los cambios del repo se ven al volver a insertar el FX.
# El JSFX va a Effects/Nube Sampler y la biblioteca de fábrica a Data/Nube Sampler/Nube (ahí también van tus samples).
set -e
RES="$HOME/Library/Application Support/REAPER"
cd "$(dirname "$0")"
mkdir -p "$RES/Effects/Nube Sampler" "$RES/Data/Nube Sampler"
ln -sf "$PWD/nube_sampler.jsfx" "$RES/Effects/Nube Sampler/nube_sampler.jsfx"
ln -sfn "$PWD/samples/Nube" "$RES/Data/Nube Sampler/Nube"
echo "Listo: en REAPER busca \"Nube Sampler\" (JS: Nube Sampler). Es un instrumento: ponlo en una pista con MIDI."
echo "Biblioteca: $RES/Data/Nube Sampler (copia ahí tus samples, o arrastra un archivo a la ventana del plugin)."
