-- Pestaña propia para los scripts de prueba (puede haber otra sesión usando el mismo REAPER):
--   local T = dofile(ROOT .. "/tab.lua"); local tab = T.open(OUT .. "/_tmp_algo.rpp")
--   ... trabajo (la pestaña activa es la propia) ...
--   T.close(tab)   -- vuelve a la propia BUSCÁNDOLA POR RUTA, la cierra y vuelve a la que estaba activa antes
-- Nunca cierra pestañas que no abrió.
local T = {}

local function find(path)
  local i = 0
  while true do
    local p, f = reaper.EnumProjects(i, "")
    if not p then return nil end
    if f == path then return p end
    i = i + 1
  end
end
T.find = find

function T.open(path)
  local prev = reaper.EnumProjects(-1, "")
  reaper.Main_OnCommand(40859, 0)                       -- nueva pestaña
  reaper.Main_SaveProjectEx(0, path, 0)                 -- con nombre propio, para encontrarla después
  reaper.Main_openProject("noprompt:" .. path)
  return {path = path, prev = prev}
end

-- Volver a la pestaña propia. Durante un render (42230) REAPER procesa mensajes y un script de OTRA sesión puede
-- arrancar en medio y cambiar la pestaña activa: llamar antes y después de cada render (y de Main_openProject).
function T.ensure(tab)
  local p = find(tab.path)
  if p and reaper.EnumProjects(-1, "") ~= p then reaper.SelectProjectInstance(p) end
  return p
end

-- render de la pestaña propia (los ajustes RENDER_* ya puestos en el proyecto 0 por quien llama, con T.ensure antes)
function T.render(tab)
  T.ensure(tab); reaper.Main_OnCommand(42230, 0); T.ensure(tab)
end

-- reabrir otro .rpp en la pestaña propia (cambia la ruta con la que se la busca)
function T.reopen(tab, rpp)
  local p = find(tab.path); if p then reaper.SelectProjectInstance(p) end
  reaper.Main_openProject("noprompt:" .. rpp); tab.path = rpp
end

function T.close(tab)
  local p = find(tab.path)
  if p then
    reaper.SelectProjectInstance(p)
    reaper.OnStopButton()
    reaper.Main_SaveProjectEx(0, tab.path, 0)          -- guardada: se cierra sin preguntar
    reaper.Main_openProject("noprompt:" .. tab.path)
    if reaper.EnumProjects(-1, "") == find(tab.path) then reaper.Main_OnCommand(40860, 0) end
  end
  if tab.prev and reaper.ValidatePtr(tab.prev, "ReaProject*") then reaper.SelectProjectInstance(tab.prev) end
end

return T
