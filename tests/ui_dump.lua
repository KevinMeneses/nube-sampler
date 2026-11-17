-- Escribe los parámetros del FX de la pista 1 de la demo en tests/out/dump.txt
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local DEMO = dofile(ROOT .. "/tab.lua").find(OUT .. "/_tmp_ui.rpp") or 0   -- la pestaña de la demo, aunque no sea la activa
local f = io.open(OUT .. "/dump.txt", "w")
local tr = reaper.GetTrack(DEMO, 0)
for p = 0, reaper.TrackFX_GetNumParams(tr, 0) - 1 do
  local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
  f:write(p + 1, " ", n, " = ", v, "\n")
end
f:write("done\n"); f:close()
