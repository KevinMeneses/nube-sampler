# Elige qué JSFX prueban los scripts (lo leen con tests/fx.lua desde tests/out/fx.txt).
# En el checkout principal: el instalado (JS:Nube Sampler/...). En un worktree: un enlace aparte a ESTE worktree
# (Effects/Nube Sampler Dev), para no cambiar el plugin que usa el usuario; tests/fxname.sh limpiar lo borra.
DEV="$HOME/Library/Application Support/REAPER/Effects/Nube Sampler Dev"
mkdir -p tests/out
if [ "$1" = limpiar ]; then
  rm -f "$DEV/nube_sampler.jsfx"; rmdir "$DEV" 2>/dev/null; rm -f tests/out/fx.txt
elif [ "$(git rev-parse --git-dir)" != "$(git rev-parse --git-common-dir)" ]; then
  mkdir -p "$DEV"; ln -sf "$PWD/nube_sampler.jsfx" "$DEV/nube_sampler.jsfx"
  echo "JS:Nube Sampler Dev/nube_sampler.jsfx" > tests/out/fx.txt
else
  echo "JS:Nube Sampler/nube_sampler.jsfx" > tests/out/fx.txt
fi
