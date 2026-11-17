-- Detiene la reproducción de la demo (para probar el teclado y los pads sin las notas del item).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local DEMO = dofile(ROOT .. "/tab.lua").find(OUT .. "/_tmp_ui.rpp") or 0   -- la pestaña de la demo, aunque no sea la activa
reaper.OnStopButtonEx(DEMO)
