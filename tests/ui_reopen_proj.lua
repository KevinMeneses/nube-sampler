-- Guarda la pestaña de demo, la vuelve a abrir desde su archivo (prueba de que el sample arrastrado se recupera) y
-- escribe los parámetros en tests/out/dump.txt.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local DEMO = dofile(ROOT .. "/tab.lua").find(OUT .. "/_tmp_ui.rpp") or 0   -- la pestaña de la demo, aunque no sea la activa
local T = dofile(ROOT .. "/tab.lua")
local tab = {path = OUT .. "/_tmp_ui.rpp"}
if DEMO ~= 0 then
  T.ensure(tab); reaper.OnStopButton()
  reaper.Main_SaveProjectEx(0, tab.path, 0); T.reopen(tab, tab.path)
  DEMO = T.find(tab.path)
end
local tr = reaper.GetTrack(DEMO, 0)
local f = io.open(OUT .. "/dump.txt", "w")
for p = 0, reaper.TrackFX_GetNumParams(tr, 0) - 1 do
  local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
  f:write(p + 1, " ", n, " = ", v, "\n")
end
f:write("done\n"); f:close()
