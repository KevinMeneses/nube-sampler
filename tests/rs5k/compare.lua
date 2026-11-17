-- Prueba clave de las zonas: el Rhodes de "Nube baja" (pista 10 del experimento: 17 RS5k, ep_036..ep_084) contra
-- Nube Sampler con las zonas armadas solas desde la carpeta. Lo lanza tests/rs5k/run.sh (copia ep_*.wav a
-- Data/Nube Sampler/zz_pruebas/ep). Escribe tests/out/rs5k_{orig,nube,nube_emb}.wav y tests/out/rs5k_log.txt.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/rs5k/[^/]*$")
local OUT = ROOT .. "/out"; local T = dofile(ROOT .. "/tab.lua"); local FX = dofile(ROOT .. "/fx.lua")
local P = dofile(ROOT .. "/params_gen.lua")
local SRC = os.getenv("HOME") .. "/Music/ClaudeBeats/trap_chill_G#m_150bpm_20261020_experimento_8lufs.rpp"
local LIB = reaper.GetResourcePath() .. "/Data/Nube Sampler/zz_pruebas/ep"
local logf = io.open(OUT .. "/rs5k_log.txt", "w")
local function log(...) local t = {} for _, v in ipairs({...}) do t[#t + 1] = tostring(v) end logf:write(table.concat(t, " "), "\n") logf:flush() end
local function norm(s, v) local mn, mx, mid = table.unpack(P.LOGP[s]); local sr = (mx - mn) / (mid - mn) - 1; local r = sr * sr
  return math.log((v - mn) / (mx - mn) * (r - 1) + 1) / math.log(r) end

-- El .rpp del usuario NO se abre: se leen del texto los bloques de los RS5k de la pista 10 y se arma una pista nueva
-- con ellos en una pestaña propia (abrir una copia en otra carpeta rompe sus rutas relativas y saca diálogos).
local fi = io.open(SRC, "rb"); local txt = fi:read("a"); fi:close()
local lines = {} for l in txt:gmatch("([^\n]*)\n?") do lines[#lines + 1] = l end
local ti, i0, i1 = 0
for i, l in ipairs(lines) do
  if l:match("^  <TRACK") then ti = ti + 1; if ti == 10 then i0 = i elseif ti == 11 then i1 = i - 1; break end end
end
local blocks, i = {}, i0
while i <= i1 do
  if lines[i]:match("^%s*BYPASS") and lines[i + 1] and lines[i + 1]:find("ReaSamplOmatic5000", 1, true) then
    local b = {lines[i]}; i = i + 1
    while i <= i1 and not (lines[i]:match("^%s*BYPASS") or lines[i]:match("^%s*>%s*$") and lines[i]:match("^(%s*)") == "    ") do
      b[#b + 1] = lines[i]; i = i + 1
    end
    blocks[#blocks + 1] = table.concat(b, "\n")
  else i = i + 1 end
end
local sname = (lines[i0 + 1] or ""):match("NAME (.*)")
local tab = T.open(OUT .. "/_rs5k_tab.rpp")
log("pista 10:", sname, "| bloques RS5k:", #blocks)
local n = 0; reaper.InsertTrackAtIndex(0, false); local tr = reaper.GetTrack(0, 0)
reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "PROJECT_SRATE_USE", 1, true)
local NOTE, GAP = 1.2, 0.6
local LEN = 2 * 22 * (NOTE + GAP) + 1
local item = reaper.CreateNewMIDIItemInProj(tr, 0, LEN, false); local take = reaper.GetActiveTake(item)
local t = 0
for _, vel in ipairs({100, 76}) do
  for p = 47, 68 do
    reaper.MIDI_InsertNote(take, false, false, reaper.MIDI_GetPPQPosFromProjTime(take, t), reaper.MIDI_GetPPQPosFromProjTime(take, t + NOTE), 0, p, vel, true)
    t = t + NOTE + GAP
  end
end
reaper.MIDI_Sort(take)
local function render(name)
  T.ensure(tab)
  os.remove(OUT .. "/" .. name .. ".wav")
  reaper.SetOnlyTrackSelected(tr)
  reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 3, true); reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
  reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true); reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", LEN, true)
  reaper.GetSetProjectInfo(0, "RENDER_SRATE", 48000, true); reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
  reaper.GetSetProjectInfo(0, "RENDER_TAILFLAG", 0, true)
  reaper.GetSetProjectInfo_String(0, "RENDER_FILE", OUT, true); reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", name, true)
  T.render(tab)
end
-- 1) los 17 RS5k tal cual
local _, ch = reaper.GetTrackStateChunk(tr, "", false)
ch = ch:gsub(">%s*$", "<FXCHAIN\nSHOW 0\nLASTSEL 0\nDOCKED 0\n" .. table.concat(blocks, "\n") .. "\n>\n>\n")
reaper.SetTrackStateChunk(tr, ch, false)
log("RS5k en la pista nueva:", reaper.TrackFX_GetCount(tr))
render("rs5k_orig")
-- 2) Nube Sampler: elegir ep_048 en el selector y "cargar la carpeta"
while reaper.TrackFX_GetCount(tr) > 0 do reaper.TrackFX_Delete(tr, 0) end
local fx = reaper.TrackFX_AddByName(tr, FX, false, -1)
local _, _, maxi = reaper.TrackFX_GetParam(tr, fx, 0); local hit
for i = 0, maxi do local _, s = reaper.TrackFX_FormatParamValue(tr, fx, 0, i, ""); if s == "zz_pruebas/ep/ep_048" then hit = i end end
if not hit then log("ERROR ep_048 no está en la biblioteca") end

reaper.TrackFX_SetParam(tr, fx, 0, hit or 0)
-- sostenido, sin filtro, calidad Alta; velocidad a volumen 37 % = (vel/127)^0.74, la curva medida del RS5k
local SET = {[21] = 1, [35] = 100, [37] = 37, [38] = 4}
for s, v in pairs(SET) do reaper.TrackFX_SetParam(tr, fx, s - 1, v) end
reaper.TrackFX_SetParamNormalized(tr, fx, 33, norm(34, 20000)); reaper.TrackFX_SetParamNormalized(tr, fx, 35, norm(36, 250))
reaper.TrackFX_SetParam(tr, fx, P.RELLIN - 1, 1)   -- relajacion lineal, como el RS5k
reaper.TrackFX_SetParam(tr, fx, P.ZLOAD - 1, 1)
local function rd(p) local _, s = reaper.TrackFX_GetFormattedParamValue(tr, fx, p - 1, ""); return s end
if (tonumber(rd(P.FRAMES)) or 0) == 0 then log("ERROR el FX no cargó audio (¿no compila?)") end
log("zonas:", rd(P.NZONES), "| modo:", rd(2), "| frames:", rd(P.FRAMES), "| MB en proyecto:", rd(P.EMBMB))
render("rs5k_nube")
-- 3) audio guardado en el proyecto, carpeta escondida, reabrir
reaper.TrackFX_SetParam(tr, fx, 61, 1)
log("con En proyecto: MB", rd(P.EMBMB))
local RPP = OUT .. "/_rs5k_emb.rpp"
local t0 = reaper.time_precise(); reaper.Main_SaveProjectEx(0, RPP, 0); local t1 = reaper.time_precise()
os.rename(LIB, LIB .. "_escondida")
T.reopen(tab, RPP); local t2 = reaper.time_precise()
tr = reaper.GetTrack(0, n); fx = 0
log("reabierto sin la carpeta: zonas", rd(P.NZONES), "| frames", rd(P.FRAMES), "| guardar", string.format("%.2f s", t1 - t0), "| abrir", string.format("%.2f s", t2 - t1))
render("rs5k_nube_emb")
os.rename(LIB .. "_escondida", LIB)
local f = io.open(RPP); log("tamaño del .rpp:", string.format("%.1f MB", f:seek("end") / 1e6)); f:close()
T.close(tab)
log("done"); logf:close()
