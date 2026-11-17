-- Detiene y cierra la pestaña de demo (la busca por su ruta, aunque no sea la activa) y vuelve a la que estaba activa
-- antes de abrirla. No toca otras pestañas.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"; local T = dofile(ROOT .. "/tab.lua")
local pf = io.open(OUT .. "/ui_prev.txt"); local prevpath = pf and pf:read("a") or ""; if pf then pf:close() end
if T.find(OUT .. "/_tmp_ui.rpp") then
  T.close({path = OUT .. "/_tmp_ui.rpp", prev = prevpath ~= "" and T.find(prevpath) or nil})
end
