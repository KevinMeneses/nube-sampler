-- Prueba de humo: carga Nube Sampler en una pestaña temporal, lista la biblioteca, renderiza una nota y cierra.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
os.execute('mkdir -p "' .. ROOT .. '"')
local f = io.open(ROOT .. "/smoke.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end f:write(table.concat(t, " "), "\n") f:flush() end
reaper.Main_OnCommand(40859, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Sampler/nube_sampler.jsfx", false, -1)
log("fx", fx, "params", reaper.TrackFX_GetNumParams(tr, fx))
local _, mn, mx = reaper.TrackFX_GetParam(tr, fx, 0)
for i = 0, mx do local _, s = reaper.TrackFX_FormatParamValue(tr, fx, 0, i, ""); log("lib", i, s) end
local function rd(p) local _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, p - 1, ""); return s end
log("slider1", rd(1), "frames", rd(160), "chops", rd(161), "det", rd(162))
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 2, false); local take = reaper.GetActiveTake(item)
reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, 0.1), reaper.MIDI_GetPPQPosFromProjTime(take, 1.5), 0, 60, 127, true)
reaper.MIDI_Sort(take)
os.remove(ROOT .. "/smoke.wav")
reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
reaper.GetSetProjectInfo_String(0, "RENDER_FILE", ROOT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "smoke", true)
reaper.Main_OnCommand(42230, 0)
log("after render nact", rd(159))
local _, chunk = reaper.GetTrackStateChunk(tr, "", false)
log((chunk:match("<JS.-\n>") or "?"):sub(1, 600))
reaper.Main_SaveProjectEx(0, ROOT .. "/_tmp_smoke.rpp", 0); reaper.Main_openProject("noprompt:" .. ROOT .. "/_tmp_smoke.rpp")
reaper.Main_OnCommand(40860, 0)
log("done") f:close()
