#!/bin/zsh
# Instala Nube Sampler en REAPER (macOS) como enlaces: los cambios del repo se ven al volver a insertar el FX.
# El JSFX va a Effects/Nube Sampler y la biblioteca de fábrica a Data/Nube Sampler/Nube (ahí también van tus samples).
# Los enlaces apuntan SIEMPRE al checkout principal del repo, aunque esto se corra desde un worktree: un worktree se
# borra al terminar y el plugin quedaba apuntando a nada (en REAPER: sin sample y mudo).
set -e
RES="$HOME/Library/Application Support/REAPER"
DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR"
if git -C "$DIR" rev-parse --git-dir >/dev/null 2>&1; then
  COMMON="$(git -C "$DIR" rev-parse --path-format=absolute --git-common-dir)"
  MAIN="$(dirname "$COMMON")"
  if [ "$MAIN" != "$DIR" ] && [ -f "$MAIN/nube_sampler.jsfx" ]; then
    echo "Esto es un worktree: enlazo al checkout principal ($MAIN), no a $DIR."
    echo "(Para probar el worktree sin tocar lo instalado: tests/fxname.sh crea JS:Nube Sampler Dev.)"
    SRC="$MAIN"
  fi
fi
mkdir -p "$RES/Effects/Nube Sampler" "$RES/Data/Nube Sampler"
ln -sf "$SRC/nube_sampler.jsfx" "$RES/Effects/Nube Sampler/nube_sampler.jsfx"
ln -sfn "$SRC/samples/Nube" "$RES/Data/Nube Sampler/Nube"
# comprobar que los enlaces llegan a algo
ok=1
[ -f "$RES/Effects/Nube Sampler/nube_sampler.jsfx" ] || { echo "ERROR: el enlace del JSFX no llega a un archivo"; ok=0; }
[ -f "$RES/Data/Nube Sampler/Nube/Keys - Rhodes C4.wav" ] || { echo "ERROR: el enlace de la biblioteca no llega a los samples"; ok=0; }
[ $ok = 1 ] || exit 1
echo "Listo: en REAPER busca \"Nube Sampler\" (JS: Nube Sampler). Es un instrumento: ponlo en una pista con MIDI."
echo "JSFX -> $SRC/nube_sampler.jsfx"
echo "Biblioteca: $RES/Data/Nube Sampler (copia ahí tus samples, o arrastra archivos a la ventana del plugin)."
