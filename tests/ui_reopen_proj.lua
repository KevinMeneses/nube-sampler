-- Guarda la pestaña de demo, la vuelve a abrir desde el archivo (prueba de que el sample arrastrado se recupera) y
-- escribe los parámetros en tests/out/dump.txt.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local tr = reaper.GetTrack(0, 0)
local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
if name == "Nube Sampler demo" then
  reaper.OnStopButton()
  reaper.Main_SaveProjectEx(0, OUT .. "/_drop.rpp", 0)
  reaper.Main_openProject("noprompt:" .. OUT .. "/_drop.rpp")
end
tr = reaper.GetTrack(0, 0)
local f = io.open(OUT .. "/dump.txt", "w")
for p = 0, reaper.TrackFX_GetNumParams(tr, 0) - 1 do
  local _, n = reaper.TrackFX_GetParamName(tr, 0, p, ""); local _, v = reaper.TrackFX_GetFormattedParamValue(tr, 0, p, "")
  f:write(p + 1, " ", n, " = ", v, "\n")
end
f:write("done\n"); f:close()
