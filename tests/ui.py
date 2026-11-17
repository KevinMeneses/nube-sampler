"""Ayudante para probar la interfaz con cliclick (ventana del FX con su tamaño por defecto, 1100 x 800 de área gráfica).
Las coordenadas son puntos dentro del área gráfica, calculadas como en @gfx (SC = 1)."""
import subprocess, time, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = "/Applications/REAPER.app/Contents/MacOS/REAPER"
HDR = 104                       # cabecera de REAPER (titulo, presets, slider del sample) sobre el área gráfica

def win():
    s = subprocess.run(["osascript", "-e", 'tell application "System Events" to tell process "REAPER" to get {position, size} of '
                        '(first window whose name contains "JS: Nube Sampler")'], capture_output=True, text=True).stdout
    x, y, w, h = [int(v) for v in s.replace(",", " ").split()]; return x, y, w, h
WX, WY, WW_, WH_ = 0, 0, 1100, 902
def locate():
    global WX, WY, WW_, WH_
    x, y, WW_, WH_ = win(); WX, WY = x, y + HDR
def pt(x, y): return f"{round(WX + x)},{round(WY + y)}"
def cc(*args): subprocess.run(["cliclick", "-w", "100", *args], check=True); time.sleep(0.35)
def focus(): cc(f"m:{pt(950, 40)}", "w:100", f"dd:{pt(950, 40)}", "w:150", f"du:{pt(950, 40)}", "w:200")     # barra superior sin controles: el primer clic tras un script solo activa la ventana
def click(x, y): focus(); cc(f"m:{pt(x, y)}", "w:150", f"dd:{pt(x, y)}", "w:200", f"du:{pt(x, y)}")
def rclick(x, y): focus(); cc(f"rc:{pt(x, y)}")
def dclick(x, y): focus(); cc(f"m:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}", f"dd:{pt(x, y)}", f"du:{pt(x, y)}")
def press(x, y): focus(); cc(f"m:{pt(x, y)}", "w:150", f"dd:{pt(x, y)}", "w:200")
def release(x, y): cc(f"du:{pt(x, y)}")
def menu(ctl, anchor, i, sub=None):
    """abre el menú del control y elige el ítem i con el mouse (ítems de 24 pt, el menú se abre debajo del control,
    en anchor). Con sub, entra al submenú del ítem i y elige el sub-ítem (los submenús se abren a la derecha, alineados)."""
    click(*ctl); time.sleep(0.6)
    ax, ay = anchor; y = ay + 14 + 24 * i
    if sub is None: cc(f"c:{pt(ax + 40, y)}"); return
    cc(f"m:{pt(ax + 40, y)}"); time.sleep(0.7); cc(f"m:{pt(ax + 330, y)}"); time.sleep(0.3)
    cc(f"m:{pt(ax + 330, y + 24 * sub)}", f"c:{pt(ax + 330, y + 24 * sub)}")
def wheel(n): subprocess.run(["swift", str(ROOT / "tests/scroll.swift"), str(n)], check=True); time.sleep(0.4)
def shot(path):
    wid = subprocess.run(["swift", str(ROOT / "tests/winid.swift"), "JS: Nube Sampler"], capture_output=True, text=True).stdout.strip()
    subprocess.run(["screencapture", "-x", "-o", f"-l{wid}", path], check=True); return path
def lua(name): subprocess.Popen([R, "-nonewinst", str(ROOT / "tests" / name)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dump():
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True); lua("ui_dump.lua")
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): return p.read_text().replace("done\n", "")
        time.sleep(0.25)
    return "(sin respuesta)"
def param(n):
    m = re.search(rf"^{n} (.*)$", dump(), re.M); return m.group(1).rsplit(" = ", 1)[1] if m else None
def num(s):
    try: return float(s.split()[0])
    except Exception: return float("nan")
def drag(x0, y0, x1, y1, steps=8):
    focus(); cc(f"m:{pt(x0, y0)}", "w:150", f"dd:{pt(x0, y0)}", "w:250")
    for k in range(1, steps + 1): cc(f"m:{pt(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)}")
    cc(f"du:{pt(x1, y1)}")
def set_sample(name):
    p = ROOT / "tests/out/set_done.txt"; p.unlink(missing_ok=True); (ROOT / "tests/out/set.txt").write_text(name + "\n"); lua("ui_set.lua")
    for _ in range(40):
        if p.exists(): break
        time.sleep(0.25)
    time.sleep(0.3)
def hover(x, y): focus(); cc(f"m:{pt(x, y)}")

# ---- layout (área gráfica de 1100 x 798 pt)
PRESETS, PRESETS_M = (270, 22), (160, 37)
CLASICO, CHOPS, ZONAS, MANTENER, ONESHOT, REMUESTREO, ESTIRAR = (421, 22), (481, 22), (541, 22), (615, 22), (687, 22), (775, 22), (855, 22)
LIB = (192, 65)
REVERSO, NORMALIZAR, AFINAR, ENPROY = (748, 65), (844, 65), (940, 65), (1036, 65)
WFX, WFY, WFW, WFVH = 14, 84, 1036, 174
def wave_x(frac): return WFX + WFW * frac
KY1, KY2, KY3, KY4 = 340, 446, 552, 658
INICIO, FIN, RAIZ = (83.3, KY1), (127.3, KY1), (259.3, KY1)
KTRK_BTN = (362.7, 297.5)
LOOPB = lambda i: (608.8 + 58 * i, 297.5)
VELOC = (803.3, KY1)
SYNC, SYNC_M = (976.7, 327), (877.3, 340)
DET = lambda i: (231.2 + 76 * i, 403.5)
PARTES = (92, KY2)
PAD = lambda i: (472.1 + (i % 8) * 50.83, 431.5 + (i // 8) * 35)
CHOP_TONO, CHOP_REV = (907.3, KY2), (1028.7, 440)
FTYPE = lambda i: (216.2 + 38 * i, 509.5)
VMODE, VMODE_M = (252, 615.5), (207, 627)
KB_Y = 755
def white(i): return (90 + 45.27 * (i + 0.5), KB_Y)
# fila 2 en Zonas (row_layout de 190 / 420 / 334 + reparto del sobrante)
Z_CARGAR, Z_AUTO, Z_QUITAR = (128.3, 426), (75.2, 450), (181.5, 450)
MAPX, MAPY, MAPW, MAPH = 258.67, 414, 438.67, 66
def map_pt(note, vel, lo=24, hi=96): return (MAPX + (note - lo + 0.5) * MAPW / (hi - lo + 1), MAPY + MAPH - (vel - 0.5) / 127 * MAPH)
Z_RAIZ, Z_DESDE, Z_HASTA, Z_VMIN, Z_VMAX = [(775.67 + 62 * i, 448) for i in range(5)]
