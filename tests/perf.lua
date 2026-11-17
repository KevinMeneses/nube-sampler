-- CPU: render de 30 s con 8 notas sostenidas (loop del pad de fábrica) en varios modos. Escribe tests/out/perf.txt.
local OUT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/out"
local FX = dofile(debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$") .. "/fx.lua")
os.execute('mkdir -p "' .. OUT .. '"')
local f = io.open(OUT .. "/perf.txt", "w")
reaper.Main_OnCommand(40859, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
local item = reaper.CreateNewMIDIItemInProj(tr, 0, 30, false); local take = reaper.GetActiveTake(item)
for k, n in ipairs({36, 48, 55, 60, 63, 67, 70, 74}) do
  reaper.MIDI_InsertNote(take, false, false, 0, reaper.MIDI_GetPPQPosFromProjTime(take, 29.5), 0, n, 100, true)
end
reaper.MIDI_Sort(take)
local IDX
local function render(name, params)
  while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
  if params then
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    if not IDX then
      local _, _, mx = reaper.TrackFX_GetParam(tr, fx, 0)
      for i = 0, mx do local _, s = reaper.TrackFX_FormatParamValue(tr, fx, 0, i, ""); if s == "Nube/Pad - Nube C3" then IDX = i end end
    end
    reaper.TrackFX_SetParam(tr, fx, 0, IDX)
    for p, v in pairs(params) do reaper.TrackFX_SetParam(tr, fx, p - 1, v) end
  end
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  local t0 = reaper.time_precise(); reaper.Main_OnCommand(42230, 0); return reaper.time_precise() - t0
end
local t0 = render("perf_vacio", nil)
local function line(label, t) f:write(string.format("%-62s %.2f %% de un nucleo\n", label, (t - t0) / 30 * 100)) end
local LOOP = {[8] = 1, [9] = 10, [10] = 90}
line("8 voces, clasico, calidad Normal (loop)", render("perf_normal", LOOP))
line("8 voces, clasico, calidad Alta (sinc, loop)", render("perf_alta", {[8] = 1, [9] = 10, [10] = 90, [21] = 1}))
line("8 voces, clasico + filtro LP 24 + lo-fi", render("perf_filtro", {[8] = 1, [9] = 10, [10] = 90, [38] = 0, [56] = 12, [57] = 26000}))
line("8 voces, estirar (WSOLA, loop)", render("perf_estirar", {[8] = 1, [9] = 10, [10] = 90, [4] = 1}))
line("8 voces, estirar + calidad Alta (peor caso)", render("perf_peor", {[8] = 1, [9] = 10, [10] = 90, [4] = 1, [21] = 1, [38] = 0}))
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_perf.rpp", 0); reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_perf.rpp"); reaper.Main_OnCommand(40860, 0)
f:write("done\n"); f:close()
