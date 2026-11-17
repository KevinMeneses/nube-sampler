-- Carga Nube Sampler en una pestaña nueva, renderiza cada caso (item MIDI + sample de tests/samples) y cierra la pestaña.
-- Uso: REAPER -nonewinst tests/render_cases.lua   (escribe tests/out/*.wav y tests/out/log.txt)
-- Solo algunos casos: patrones Lua separados por espacios en tests/out/only.txt (REAPER no ve las variables de la terminal).
-- Las señales tienen que estar en REAPER/Data/Nube Sampler/zz_pruebas (lo hace tests/run.sh).
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/[^/]*$")
local OUT = ROOT .. "/out"
local FX = "JS:Nube Sampler/nube_sampler.jsfx"
local LIB = reaper.GetResourcePath() .. "/Data/Nube Sampler/zz_pruebas"
local P = dofile(ROOT .. "/params_gen.lua")
os.execute('mkdir -p "' .. OUT .. '"')
local logf = io.open(OUT .. "/log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t+1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end
local of = io.open(OUT .. "/only.txt"); local only = of and of:read("l") or nil; if of then of:close() end
if only == "" then only = nil end

local function to_norm(s, v)
  local mn, mx, mid = table.unpack(P.LOGP[s])
  local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r)
end
local function with(a, b) local r = {} for k, v in pairs(a) do r[k] = v end for k, v in pairs(b or {}) do r[k] = v end return r end
local function chop(k, what) return P.CHOP0 + 3 * (k - 1) + what end   -- what: 0 tono, 1 ganancia, 2 reverso

local B = {[37] = 0}                                   -- sin sensibilidad a la velocidad, todo lo demás por defecto
local N = function(t0, t1, p, v) return {t0, t1, p, v or 127} end
local C4 = {N(0.1, 1.3, 60)}
local Z = "zz_pruebas/"

-- {nombre, sample, notas, parámetros, largo (s), CC, opciones}
local CASES = {
  {"null_noise", "noise_st", C4, B, 1.5},
  {"onset", "noise_st", {N(0.5, 1.2, 60)}, B, 1.3},
  {"srconv", "sine220_44k", {N(0.1, 1.15, 60)}, B, 1.2},
  {"kt_oct", "sine440", {N(0.1, 1.5, 72)}, B, 1.7},
  {"kt_fifth", "sine440", {N(0.1, 1.5, 67)}, B, 1.7},
  {"kt_off", "sine440", {N(0.1, 1.5, 72)}, with(B, {[15] = 0}), 1.7},
  {"root", "sine440", {N(0.1, 1.5, 69)}, with(B, {[14] = 69}), 1.7},
  {"tono", "sine440", {N(0.1, 1.5, 60)}, with(B, {[16] = -12}), 1.7},
  {"fino", "sine440", {N(0.1, 1.5, 60)}, with(B, {[17] = 50}), 1.7},
  {"startend", "ramp", C4, with(B, {[5] = 25, [6] = 50}), 1.5},
  {"reverse", "ramp", C4, with(B, {[7] = 1}), 1.5},
  {"loop_fwd", "sine440", {N(0.1, 4.1, 60)}, with(B, {[8] = 1, [9] = 25, [10] = 75}), 4.5},
  {"loop_noxf", "sine440", {N(0.1, 3.1, 60)}, with(B, {[8] = 1, [9] = 25.013, [10] = 74.987, [11] = 0}), 3.3},
  {"loop_xf", "sine440", {N(0.1, 3.1, 60)}, with(B, {[8] = 1, [9] = 25.013, [10] = 74.987, [11] = 30}), 3.3},
  {"pingpong", "ramp", {N(0.1, 3.1, 60)}, with(B, {[8] = 2, [9] = 20, [10] = 80}), 3.3},
  {"oneshot", "sine440", {N(0.1, 0.15, 60)}, with(B, {[3] = 1}), 2.4},
  {"gate", "sine440", {N(0.1, 0.15, 60)}, B, 2.4},
  {"fades", "sine440", {N(0.1, 1.5, 60)}, with(B, {[6] = 50, [12] = 100, [13] = 200}), 1.5},
  {"vel", "sine440", {N(0.1, 0.6, 60, 127), N(0.8, 1.3, 60, 64)}, with(B, {[37] = 100}), 1.5},
  {"vel0", "sine440", {N(0.1, 0.6, 60, 127), N(0.8, 1.3, 60, 64)}, B, 1.5},
  {"env_a", "sine440", {N(0.1, 1.0, 60)}, with(B, {[33] = 100}), 1.2},
  {"env_ds", "sine440", {N(0.1, 1.2, 60)}, with(B, {[34] = 200, [35] = 50}), 1.3},
  {"env_r", "sine440", {N(0.1, 0.5, 60)}, with(B, {[36] = 300}), 1.4},
  {"flt_off", "saw_c4", C4, B, 1.4},
  {"flt_lp24", "saw_c4", C4, with(B, {[38] = 0, [39] = 1000}), 1.4},
  {"flt_lp12", "saw_c4", C4, with(B, {[38] = 1, [39] = 1000}), 1.4},
  {"flt_bp", "saw_c4", C4, with(B, {[38] = 2, [39] = 1000}), 1.4},
  {"flt_hp", "saw_c4", C4, with(B, {[38] = 3, [39] = 1000}), 1.4},
  {"flt_reso", "saw_c4", C4, with(B, {[38] = 1, [39] = 1000, [40] = 80}), 1.4},
  {"env2cut", "saw_c4", C4, with(B, {[38] = 0, [39] = 200, [42] = 60, [44] = 300}), 1.4},
  {"drive", "sine440", C4, with(B, {[41] = 12}), 1.4},
  {"env2tono", "sine440", {N(0.1, 1.2, 60)}, with(B, {[47] = 12, [44] = 100}), 1.3},
  {"poly", "sine440", {N(0.1, 1.5, 60), N(0.1, 1.5, 64), N(0.1, 1.5, 67)}, with(B, {[60] = -12}), 1.7},
  {"voices2", "sine440", {N(0.1, 1.5, 60), N(0.2, 1.5, 64), N(0.3, 1.5, 67)}, with(B, {[29] = 2}), 1.7},
  {"retrig", "sine440", {N(0.1, 0.29, 60), N(0.3, 0.9, 60)}, B, 1.2},
  {"mono", "sine440", {N(0.1, 1.4, 60), N(0.3, 0.8, 64)}, with(B, {[28] = 1}), 1.6},
  {"glide_leg", "sine440", {N(0.1, 0.65, 57), N(0.6, 1.3, 69)}, with(B, {[28] = 2, [30] = 200}), 1.5},
  {"glide_mono", "sine440", {N(0.1, 0.5, 57), N(0.6, 1.3, 69)}, with(B, {[28] = 1, [30] = 200}), 1.5},
  {"glide_leg_sep", "sine440", {N(0.1, 0.5, 57), N(0.6, 1.3, 69)}, with(B, {[28] = 2, [30] = 200}), 1.5},
  {"legato_pos", "ramp", {N(0.1, 0.65, 57), N(0.6, 1.0, 69)}, with(B, {[28] = 2, [15] = 0}), 1.2},
  {"mono_pos", "ramp", {N(0.1, 0.65, 57), N(0.6, 1.0, 69)}, with(B, {[28] = 1, [15] = 0}), 1.2},
  {"bend", "sine440", C4, B, 1.4, {{0.05, 0xE0, 127, 127}}},
  {"modwheel", "sine440", C4, B, 1.4, {{0.05, 0xB0, 1, 127}}},
  {"pedal", "sine440", {N(0.1, 0.3, 60)}, B, 1.4, {{0.05, 0xB0, 64, 127}, {0.8, 0xB0, 64, 0}}},
  {"ch_equal", "ramp", {N(0.1, 0.12, 36), N(0.6, 0.62, 38)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 4}), 1.0},
  {"ch_trans", "hits8", {}, with(B, {[2] = 1, [3] = 1, [22] = 0}), 2.6},
  {"ch_loop", "../Nube/Loop - Chill 90 BPM 4 compases", {N(0.1, 0.2, 36)}, with(B, {[2] = 1, [22] = 0}), 0.3},
  {"ch_sens0", "hits8", {N(0.1, 0.2, 36)}, with(B, {[2] = 1, [22] = 0, [23] = 0}), 0.3},
  {"ch_thru", "ramp", {N(0.1, 0.12, 42)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 8, [26] = 1}), 0.6},
  {"ch_nothru", "ramp", {N(0.1, 0.12, 42)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 8}), 0.6},
  {"ch_choke", "ramp", {N(0.1, 0.12, 36), N(0.2, 0.22, 37)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 4, [27] = 1}), 0.6},
  {"ch_nochoke", "ramp", {N(0.1, 0.12, 36), N(0.2, 0.22, 37)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 4}), 0.6},
  {"ch_params", "sine440", {N(0.1, 0.5, 36), N(0.6, 1.0, 37), N(1.1, 1.5, 38)},
     with(B, {[2] = 1, [22] = 1, [24] = 4, [chop(2, 0)] = 12, [chop(3, 1)] = -6}), 1.6},
  {"ch_rev", "ramp", {N(0.1, 0.4, 37)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 4, [chop(2, 2)] = 1}), 0.6},
  {"ch_base", "ramp", {N(0.1, 0.12, 60)}, with(B, {[2] = 1, [3] = 1, [22] = 1, [24] = 4, [25] = 60}), 0.5},
  {"st_slow", "sine440", {N(0.1, 4.6, 60)}, with(B, {[4] = 1, [18] = 50}), 4.8},
  {"st_pitch", "sine440", {N(0.1, 2.6, 72)}, with(B, {[4] = 1}), 2.8},
  {"st_loop", "loop100", {N(0.1, 5.0, 60)}, with(B, {[4] = 1, [15] = 0}), 5.2},
  {"sync_vinyl", "loop100", {N(0.0, 4.5, 60)}, with(B, {[19] = 4, [15] = 0}), 4.6, nil, {bpm = 120}},
  {"sync_stretch", "loop100", {N(0.0, 4.5, 60)}, with(B, {[4] = 1, [19] = 4, [15] = 0}), 4.6, nil, {bpm = 120}},
  {"q_normal", "sine15k", {N(0.1, 0.9, 72)}, B, 1.0},
  {"q_alta", "sine15k", {N(0.1, 0.9, 72)}, with(B, {[21] = 1}), 1.0},
  {"q_alta_pass", "sine5k", {N(0.1, 0.9, 72)}, with(B, {[21] = 1}), 1.0},
  {"q_alta_down", "sine5k", {N(0.1, 0.9, 48)}, with(B, {[21] = 1}), 1.0},
  {"normalize", "quiet", C4, with(B, {[61] = 1}), 1.3},
  {"nonorm", "quiet", C4, B, 1.3},
  {"pan", "sine440", C4, with(B, {[58] = 50}), 1.4},
  {"width0", "noise_st", C4, with(B, {[59] = 0}), 1.4},
  {"width200", "noise_st", C4, with(B, {[59] = 200}), 1.4},
  {"volume", "sine440", C4, with(B, {[60] = -6}), 1.4},
  {"bits4", "sine440", C4, with(B, {[56] = 4}), 1.4},
  {"srred", "sine440", C4, with(B, {[57] = 6000}), 1.4},
  {"lfo_vol", "sine440", C4, with(B, {[53] = 2, [54] = 100, [51] = 4}), 1.4},
  {"lfo_pan", "sine440", C4, with(B, {[53] = 3, [54] = 100, [51] = 3}), 1.4},
  {"lfo_pitch", "sine440", C4, with(B, {[53] = 0, [54] = 10, [51] = 5}), 1.4},
  {"det_off30", "sine_off30", C4, B, 0.3},
  {"det_saw", "saw_c4", C4, B, 0.3},
  {"det_44k", "sine220_44k", C4, B, 0.3},
  {"reopen_a", "noise_st", C4, with(B, {[16] = 3, [38] = 1, [39] = 2000}), 1.4},
  {"reopen_b", "noise_st", C4, with(B, {[16] = 3, [38] = 1, [39] = 2000}), 1.4, nil, {reopen = true}},
  {"embed", "noise_st", C4, with(B, {[16] = 3, [38] = 1, [39] = 2000, [62] = 1}), 1.4, nil, {reopen = true, hide = true}},
  {"noembed", "noise_st", C4, with(B, {[16] = 3, [38] = 1, [39] = 2000}), 1.4, nil, {reopen = true, hide = true}},
  {"stress", "../Nube/Keys - Rhodes C4", {}, with(B, {[36] = 2000}), 3},
  {"stress_st", "../Nube/Loop - Chill 90 BPM 4 compases", {}, with(B, {[4] = 1, [29] = 8}), 3},
}
for k = 0, 7 do table.insert(CASES[#CASES][3], N(0.05 + k * 0.3, 0.05 + k * 0.3 + 0.8, 48 + (k * 5) % 24)) end
for k = 0, 23 do table.insert(CASES[#CASES - 1][3], N(0.05 + k * 0.06, 0.05 + k * 0.06 + 0.3, 48 + (k * 7) % 24)) end
for _, c in ipairs(CASES) do if c[1] == "ch_trans" then for k = 0, 7 do table.insert(c[3], N(0.1 + k * 0.3, 0.15 + k * 0.3, 36 + k)) end end end   -- un chop cada 0.3 s
-- cada preset con el loop de fábrica: notas graves (chops) y un acorde
local PHRASE = {N(0.0, 0.5, 36, 100), N(0.5, 1.0, 38, 100), N(1.0, 1.5, 41, 100), N(1.6, 3.0, 60, 100), N(1.6, 3.0, 64, 100), N(1.6, 3.0, 67, 100)}
for p = 1, P.NPRESETS do CASES[#CASES + 1] = {"preset" .. p, "../Nube/Loop - Chill 90 BPM 4 compases", PHRASE, {[P.PRESET] = p}, 4} end

reaper.Main_OnCommand(40859, 0) -- nueva pestaña
local function setup_project(bpm)
  reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true)
  reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
  reaper.SetCurrentBPM(0, bpm or 120, false)
end
setup_project()
reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)

-- índice de cada archivo de la biblioteca en el slider 1
local fx0 = reaper.TrackFX_AddByName(tr, FX, false, -1)
if fx0 < 0 then log("ERROR no cargó el FX") end
local IDX = {}
local _, _, maxi = reaper.TrackFX_GetParam(tr, fx0, 0)
for i = 0, maxi do local _, s = reaper.TrackFX_FormatParamValue(tr, fx0, 0, i, ""); IDX[s] = i end
reaper.TrackFX_Delete(tr, fx0)

local function render(name)
  local file = OUT .. "/" .. name .. ".wav"
  os.remove(file)
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
  reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 1, true)
  reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true)
  reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
  reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  reaper.Main_OnCommand(42230, 0)
end
local function rd(fx, p) local _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, p - 1, ""); return s end

for _, c in ipairs(CASES) do
  local name, smp, notes, params, len, ccs, opt = c[1], c[2], c[3], c[4], c[5], c[6] or {}, c[7] or {}
  local pick = not only
  if only then for w in only:gmatch("%S+") do if name:find(w) then pick = true end end end
  if pick then
    setup_project(opt.bpm)
    while reaper.CountTrackMediaItems(tr) > 0 do reaper.DeleteTrackMediaItem(tr, reaper.GetTrackMediaItem(tr, 0)) end
    local item = reaper.CreateNewMIDIItemInProj(tr, 0, len, false)
    local take = reaper.GetActiveTake(item)
    for _, n in ipairs(notes) do
      reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, n[1]),
        reaper.MIDI_GetPPQPosFromProjTime(take, n[2]), 0, n[3], n[4], true)
    end
    for _, e in ipairs(ccs) do
      reaper.MIDI_InsertCC(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, e[1]), e[2], 0, e[3], e[4])
    end
    reaper.MIDI_Sort(take)
    while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
    local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
    local key = smp:sub(1, 3) == "../" and smp:sub(4) or Z .. smp
    if not IDX[key] then log("ERROR no está en la biblioteca:", key) end
    reaper.TrackFX_SetParam(tr, fx, 0, IDX[key] or 0)
    if params[P.PRESET] then reaper.TrackFX_SetParam(tr, fx, P.PRESET - 1, params[P.PRESET]) end
    for s, v in pairs(params) do
      if s ~= P.PRESET then
        if P.LOGP[s] then reaper.TrackFX_SetParamNormalized(tr, fx, s - 1, to_norm(s, v))
        else reaper.TrackFX_SetParam(tr, fx, s - 1, v) end
      end
    end
    local hidden
    if opt.reopen then
      local rpp = OUT .. "/_reopen_" .. name .. ".rpp"
      reaper.Main_SaveProjectEx(0, rpp, 0)
      if opt.hide then hidden = LIB .. "/" .. smp .. ".wav"; os.rename(hidden, hidden .. ".escondido") end
      reaper.Main_openProject("noprompt:" .. rpp)
      tr = reaper.GetTrack(0, 0); fx = 0
    end
    render(name)
    if hidden then os.rename(hidden .. ".escondido", hidden) end
    log("caso", name, "| frames", rd(fx, P.FRAMES), "| chops", rd(fx, P.NCHOPS), "| nota", rd(fx, P.DETECT), "| sample", rd(fx, 1))
  end
end
reaper.Main_SaveProjectEx(0, OUT .. "/_tmp_test.rpp", 0)
reaper.Main_openProject("noprompt:" .. OUT .. "/_tmp_test.rpp")
reaper.Main_OnCommand(40860, 0) -- cerrar pestaña
log("done")
logf:close()
