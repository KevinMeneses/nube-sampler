local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/probe/[^/]*$")
local OUT = ROOT .. "/out"; local T = dofile(ROOT .. "/tab.lua")
local log = io.open(OUT .. "/ser_log.txt", "w")
local tab = T.open(OUT .. "/_tmp_ser.rpp")
for _, n in ipairs({4500000, 16000000}) do
  while reaper.CountTracks(0) > 0 do reaper.DeleteTrack(reaper.GetTrack(0, 0)) end
  reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
  local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Sampler Dev/ser_probe.jsfx", false, -1)
  reaper.TrackFX_SetParam(tr, fx, 0, n)
  local rpp = OUT .. "/_ser_" .. n .. ".rpp"
  local t0 = reaper.time_precise(); reaper.Main_SaveProjectEx(0, rpp, 0); local t1 = reaper.time_precise()
  T.reopen(tab, rpp); local t2 = reaper.time_precise()
  tr = reaper.GetTrack(0, 0)
  local s = 0
  local got = tr and reaper.TrackFX_GetParam(tr, 0, 1) or -1; local gn = tr and reaper.TrackFX_GetParam(tr, 0, 2) or -1
  local f = io.open(rpp); local sz = f:seek("end"); f:close()
  log:write(string.format("n %d (%.1f s a 48k) | leidos %d | error max %.3f e-6 (%d) | rpp %.1f MB | guardar %.1f s abrir %.1f s\n", n, n / 48000, gn, got, s, sz / 1e6, t1 - t0, t2 - t1))
  log:flush()
end
T.close(tab)
log:write("done\n"); log:close()
