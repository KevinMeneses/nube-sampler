-- Abre el FX a probar flotante en una pestaña propia (para ver errores de compilación). Cerrar con err_close.lua.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/probe/[^/]*$")
local OUT = ROOT .. "/out"; local T = dofile(ROOT .. "/tab.lua")
local _, prevpath = reaper.EnumProjects(-1, "")
T.open(OUT .. "/_tmp_err.rpp")
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local fx = reaper.TrackFX_AddByName(tr, dofile(ROOT .. "/fx.lua"), false, -1)
reaper.TrackFX_Show(tr, fx, 3)
local f = io.open(OUT .. "/err.txt", "w"); f:write(prevpath or "", "\ndone\n"); f:close()
