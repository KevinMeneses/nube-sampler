-- Abre una pestaña de demo: pista con un patrón MIDI en loop (fader en -inf, no suena), Nube Sampler con un sample y un
-- preset, ventana del FX flotante y reproducción en loop para ver las gráficas. Cerrar con tests/ui_close.lua.
-- Opciones (REAPER no ve las variables de la terminal): tests/out/demo_opts.txt = "preset sample..." (el sample puede tener espacios)
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local o = io.open(ROOT .. "/out/demo_opts.txt"); local txt = o and o:read("a") or ""; if o then o:close() end
local preset, sample = txt:match("^%s*(%d+)%s+(.-)%s*$")
preset = tonumber(preset) or 7; sample = (sample and #sample > 0) and sample or "Nube/Loop - Chill 90 BPM 4 compases"
reaper.Main_OnCommand(40859, 0)
reaper.SetCurrentBPM(0, 90, false)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "Nube Sampler demo", true)
reaper.SetMediaTrackInfo_Value(tr, "D_VOL", 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 16 * 60 / 90, false); local take = reaper.GetActiveTake(item)
local function note(t0, t1, p, v) reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, t0), reaper.MIDI_GetPPQPosFromProjTime(take, t1), 0, p, v, true) end
local beat = 60 / 90
local pat = {36, 37, 38, 37, 39, 37, 40, 41, 36, 37, 42, 37, 43, 44, 45, 46}
for k, p in ipairs(pat) do note((k - 1) * beat, (k - 1) * beat + beat * 0.9, p, 100) end
for _, p in ipairs({60, 64, 67}) do note(8 * beat, 15.5 * beat, p, 90) end
reaper.MIDI_Sort(take)
local fx = reaper.TrackFX_AddByName(tr, "JS:Nube Sampler/nube_sampler.jsfx", false, -1)
local _, _, mx = reaper.TrackFX_GetParam(tr, fx, 0)
for i = 0, mx do local _, s = reaper.TrackFX_FormatParamValue(tr, fx, 0, i, ""); if s == sample then reaper.TrackFX_SetParam(tr, fx, 0, i) end end
if preset > 0 then reaper.TrackFX_SetParam(tr, fx, 158, preset) end
reaper.TrackFX_Show(tr, fx, 3)
reaper.GetSet_LoopTimeRange(true, true, 0, 16 * beat, false)
reaper.SetEditCurPos(0, false, false)
reaper.GetSetRepeat(1)
reaper.OnPlayButton()
local f = io.open(ROOT .. "/out/ui.txt", "w"); f:write("done\n"); f:close()
