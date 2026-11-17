"""Pruebas de la interfaz con el mouse. Requiere la demo abierta (tests/reopen.sh): loop de fábrica + preset 7 (Chops MPC).
No correr si alguien está usando la computadora (mueve el mouse de verdad)."""
import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from ui import *
OUT = os.environ.get("NUBE_SHOTS", str(ROOT / "tests/out"))
fails = 0
def held(x, y):
    """aprieta y espera 1 voz; si el clic no llegó a la interfaz (lee el mouse a 60 Hz), suelta y reintenta una vez"""
    press(x, y); v = voices_settle(1.0)
    if v != 1.0: release(x, y); voices_settle(0.0); press(x, y); v = voices_settle(1.0)
    return v
def voices_settle(want, timeout=2.0):
    """notas sonando (lectura), esperando hasta timeout a que llegue a want (la cola de REAPER puede tardar un bloque)"""
    t0 = time.time(); v = num(param(160))
    while v != want and time.time() - t0 < timeout: time.sleep(0.25); v = num(param(160))
    return v
def check(name, got, want):
    global fails
    ok = (want(got) if callable(want) else got == want); fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:58s} {got!r}")

subprocess.run(["osascript", "-e", 'tell application "REAPER" to activate']); time.sleep(0.6)
locate(); focus(); time.sleep(0.5); focus(); time.sleep(0.5)   # calentamiento: el primer clic solo activa la ventana
check("arranca en Chops con el loop (32 chops)", (param(2), num(param(162))), ("Chops", 32.0))
click(*CLASICO); check("boton Clasico", param(2), "Clasico")
click(*ESTIRAR); check("boton Estirar", param(4), "Estirar")
click(*REMUESTREO); check("boton Remuestreo", param(4), "Remuestreo")
click(*MANTENER); check("boton Mantener", param(3), "Mantener")
x, y = INICIO; drag(x, y, x, y - 30)
check("arrastrar Inicio hacia arriba lo sube", num(param(5)), lambda v: v > 0.5)
dclick(x, y); check("doble clic en Inicio = 0 %", num(param(5)), 0.0)
drag(WFX + 5, WFY + 6, wave_x(0.25) + 5, WFY + 6, steps=10)
check("arrastrar la bandera S en la onda (~25 %)", num(param(5)), lambda v: 22 < v < 28)
dclick(wave_x(0.25) + 5, WFY + 6); check("doble clic en la bandera S = 0 %", num(param(5)), 0.0)
click(*KTRK_BTN); check("boton Sigue teclado -> Tono fijo", param(15), "No")
click(*KTRK_BTN)
click(*LOOPB(1)); check("loop Adelante", param(8), "Adelante")
menu(SYNC, SYNC_M, 5); check("menu A tempo -> 4 compases", param(19), "4 compases")
menu(SYNC, SYNC_M, 0); check("menu A tempo -> Apagado", param(19), "Apagado")
click(*CHOPS); click(*DET(1))
check("Chops en partes iguales: 8 chops", (param(22), num(param(162))), ("Partes iguales", 8.0))
hover(*PARTES); wheel(1); check("rueda sobre Partes: 8 -> 9", (num(param(24)), num(param(162))), (9.0, 9.0))
dclick(wave_x(0.30), WFY + 90)
check("doble clic en la onda: corte nuevo (pasa a A mano)", (param(22), num(param(162))), ("A mano", 10.0))
rclick(wave_x(0.30), WFY + 90); check("clic derecho en el corte lo quita", num(param(162)), 9.0)
lua("ui_stop.lua"); time.sleep(1.0)
for _ in range(10):
    if num(param(160)) == 0: break
    time.sleep(0.4)
check("detenido: no suena nada", num(param(160)), 0.0)
check("pad 3 apretado: suena 1 voz", held(*PAD(2)), 1.0)
release(*PAD(2)); check("pad soltado (Mantener): se apaga", voices_settle(0.0), 0.0)
hover(*CHOP_TONO); wheel(2); check("rueda sobre el tono del chop 3: +2 st", num(param(63 + 3 * 2)), 2.0)
click(*CHOP_REV); check("reverso del chop 3", param(65 + 3 * 2), "Si")
click(*CLASICO)
check("clic sostenido en la onda: escucha desde ahi", held(wave_x(0.5), WFY + 90), 1.0)
release(wave_x(0.5), WFY + 90); check("al soltar se apaga", voices_settle(0.0), 0.0)
check("tecla en pantalla: suena", held(*white(7)), 1.0)
release(*white(7)); check("tecla soltada: se apaga", voices_settle(0.0), 0.0)
set_sample("Nube/Kalimba C5"); check("selector Sample (REAPER) -> Kalimba C5", param(1), "Nube/Kalimba C5")
click(*AFINAR); check("Afinar: raiz 72 (C5), fino ~0 (kalimba en 523.25 Hz)", (num(param(14)), round(num(param(17)))), (72.0, 0))
menu(PRESETS, PRESETS_M, 5, 0); check("menu presets -> Lo-fi -> SP 12 bits", num(param(56)), 12.0)
# arrastrar un archivo de afuera (opcional: el arrastre sintético de macOS no siempre llega a soltar)
if os.environ.get("NUBE_DROP"):
    # arrastrar un archivo de afuera (fuera de la biblioteca) a la forma de onda
    import shutil
    dd = ROOT / "tests/out/arrastre"; dd.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "tests/samples/loop100.wav", dd / "Mi loop 100 BPM.wav")
    src = subprocess.Popen(["swift", str(ROOT / "tests/dragsrc.swift"), str(dd / "Mi loop 100 BPM.wav"), "1300", "500"], stdout=subprocess.PIPE, text=True)
    src.stdout.readline(); time.sleep(0.8)
    tx, ty = pt(wave_x(0.5), WFY + 90).split(",")
    cc("m:1340,540", "dd:1340,540")
    for k in range(1, 13): cc(f"m:{1340 + (int(tx) - 1340) * k // 12},{540 + (int(ty) - 540) * k // 12}")
    time.sleep(0.4); cc(f"du:{tx},{ty}"); time.sleep(1.5); src.kill()
    check("arrastrar un archivo a la ventana lo carga (230400 frames)", num(param(161)), 230400.0)
    p = ROOT / "tests/out/dump.txt"; p.unlink(missing_ok=True); lua("ui_reopen_proj.lua")
    for _ in range(40):
        if p.exists() and "done" in p.read_text(): break
        time.sleep(0.25)
    m = re.search(r"^161 .* = (.*)$", p.read_text(), re.M)
    check("guardar y reabrir: el archivo arrastrado sigue cargado", num(m.group(1)) if m else None, 230400.0)
time.sleep(0.5); shot(f"{OUT}/ui_final.png")
print("FALLAS:", fails)
sys.exit(1 if fails else 0)
