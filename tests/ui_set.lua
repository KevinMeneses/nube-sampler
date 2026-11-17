-- Elige un sample de la biblioteca en el FX de la pista 1 (como el selector Sample de REAPER).
-- El nombre va en tests/out/set.txt (REAPER no ve las variables de la terminal).
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local f = io.open(OUT .. "/set.txt"); local name = f:read("l"); f:close()
local tr = reaper.GetTrack(0, 0)
local _, _, mx = reaper.TrackFX_GetParam(tr, 0, 0)
for i = 0, mx do local _, s = reaper.TrackFX_FormatParamValue(tr, 0, 0, i, ""); if s == name then reaper.TrackFX_SetParam(tr, 0, 0, i) end end
local d = io.open(OUT .. "/set_done.txt", "w"); d:write("done\n"); d:close()
