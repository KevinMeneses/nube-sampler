"""Pruebas de mouse de las zonas. Requiere la demo con los 17 ep_* en zonas (tests/ui_zones.sh la prepara).
No correr si alguien está usando la computadora (mueve el mouse de verdad)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
P = {k: int(v) for k, v in re.findall(r"(\w+) = (\d+)", (ROOT / "tests/params_gen.lua").read_text())}
fails = 0
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:58s} {got!r}")
def zsel(): return tuple(num(param(P[k])) for k in ("ZSEL", "ZROOT", "ZLO", "ZHI"))
def voices_settle(want, timeout=2.0):
    t0 = time.time(); v = num(param(P["NACT"]))
    while v != want and time.time() - t0 < timeout: time.sleep(0.25); v = num(param(P["NACT"]))
    return v

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
locate(); focus(); time.sleep(0.5); focus(); time.sleep(0.5)
lua("ui_stop.lua"); time.sleep(1.0)
check("demo: modo Zonas con 17 zonas", (param(2), num(param(P["NZONES"]))), ("Zonas", 17.0))
check("zona 1 = ep_036 (raiz 36, 0-37)", zsel(), (1.0, 36.0, 0.0, 37.0))
click(*map_pt(60, 64)); check("clic en el mapa (nota 60): zona 9 = ep_060, 59-61", zsel(), (9.0, 60.0, 59.0, 61.0))
hover(*Z_HASTA); wheel(1); check("rueda sobre Hasta: 61 -> 62", zsel()[3], 62.0)
x, y = Z_DESDE; drag(x, y, x, y - 14, steps=6); check("arrastrar Desde hacia arriba: 59 -> 61", zsel()[2], 61.0)
dclick(*Z_DESDE); check("doble clic en Desde = rangos automaticos (59-61)", zsel()[2:], (59.0, 61.0))
hover(*Z_RAIZ); wheel(-1); check("rueda sobre Raiz: 60 -> 59", zsel()[1], 59.0)
dclick(*Z_RAIZ); check("doble clic en Raiz = la del nombre (60)", zsel()[1], 60.0)
click(*Z_QUITAR); check("Quitar zona: quedan 16", num(param(P["NZONES"])), 16.0)
click(*Z_AUTO); check("Rangos auto: la zona 9 ahora es ep_063 con 61-64", zsel(), (9.0, 63.0, 61.0, 64.0))
click(*Z_CARGAR); check("Cargar la carpeta: vuelven las 17", num(param(P["NZONES"])), 17.0)
click(wave_x(4.5 / 17), WFY + 90); check("clic en la onda sobre la 5a zona: ep_048", zsel()[:2], (5.0, 48.0))
voices_settle(0.0)
press(*white(7)); check("tecla en pantalla: suena 1 voz", voices_settle(1.0), 1.0)
release(*white(7)); check("tecla soltada: se apaga", voices_settle(0.0), 0.0)
click(681.3, 509.5); check("boton de relajacion -> Lineal", param(P["RELLIN"]), "Lineal (como RS5k)")
click(681.3, 509.5); check("boton de relajacion -> Exponencial", param(P["RELLIN"]), "Exponencial")
click(*ENPROY); check("En proyecto: si, ~21 MB", (param(62), round(num(param(P["EMBMB"])))), ("Si", 21))
click(*CLASICO); check("boton Clasico", param(2), "Clasico")
click(*ZONAS); check("boton Zonas: siguen las 17", (param(2), num(param(P["NZONES"]))), ("Zonas", 17.0))
click(*map_pt(60, 64)); time.sleep(0.6); shot(f"{OUT}/ui_zonas.png")
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
