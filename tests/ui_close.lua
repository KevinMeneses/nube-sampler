-- Detiene y cierra la pestaña de demo sin preguntar (solo si la pestaña activa es la demo).
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local tr = reaper.GetTrack(0, 0)
local name = ""
if tr then _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false) end
if name == "Nube Sampler demo" then
  reaper.OnStopButton()
  reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_ui.rpp", 0)
  reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_ui.rpp")
  reaper.Main_OnCommand(40860, 0)
end
