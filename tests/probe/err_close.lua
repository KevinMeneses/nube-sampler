-- Cierra la pestaña de err_open.lua (buscándola por su ruta) y vuelve a la pestaña activa que haya.
local ROOT = debug.getinfo(1, "S").source:match("^@(.*)/probe/[^/]*$")
local OUT = ROOT .. "/out"; local T = dofile(ROOT .. "/tab.lua")
local path = OUT .. "/_tmp_err.rpp"
local fr = io.open(OUT .. "/err.txt"); local prevpath = fr and fr:read("l") or ""; if fr then fr:close() end
local p = T.find(path)
if p then
  local tr = reaper.GetTrack(p, 0); if tr then reaper.TrackFX_Show(tr, 0, 2) end
  T.close({path = path, prev = prevpath ~= "" and T.find(prevpath) or nil})
end
local f = io.open(OUT .. "/err.txt", "w"); f:write("closed\n"); f:close()
