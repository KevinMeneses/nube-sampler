-- nombre del FX a probar (lo escribe tests/fxname.sh; por defecto el instalado)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local f = io.open(ROOT .. "/out/fx.txt"); local s = f and f:read("l"); if f then f:close() end
return (s and s ~= "") and s or "JS:Nube Sampler/nube_sampler.jsfx"
