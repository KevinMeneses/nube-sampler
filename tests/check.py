"""Compara los renders de tests/out con lo que dice la teoría. Sale con código 1 si algo falla."""
import numpy as np, soundfile as sf, pathlib, re, sys
from scipy import signal as sg
D = pathlib.Path(__file__).parent / "out"; S = pathlib.Path(__file__).parent / "samples"; SR = 48000
def db(x): return 20 * np.log10(np.abs(x) + 1e-15)
def mtof(n): return 440 * 2 ** ((n - 69) / 12)
def load(name):
    x, sr = sf.read(D / f"{name}.wav"); assert sr == SR; return x
def src(name): return sf.read(S / f"{name}.wav")[0]
def I(t): return int(round(t * SR))
def seg(x, t0, t1): return x[I(t0):I(t1)]
def tone(x, f, t0, t1):
    """amplitud (dB) de la componente f por mínimos cuadrados"""
    s = seg(x, t0, t1); tt = np.arange(I(t0), I(t0) + len(s)) / SR
    M = np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1)
    c, *_ = np.linalg.lstsq(M, s, rcond=None); return db(np.hypot(*c))
def tones(x, fs, t0, t1):
    """amplitudes (dB) de varias componentes a la vez (sin fuga de unas en otras)"""
    s = seg(x, t0, t1); tt = np.arange(I(t0), I(t0) + len(s)) / SR
    M = np.concatenate([np.stack([np.sin(2 * np.pi * f * tt), np.cos(2 * np.pi * f * tt)], 1) for f in fs], 1)
    c, *_ = np.linalg.lstsq(M, s, rcond=None); return np.array([db(np.hypot(c[2 * i], c[2 * i + 1])) for i in range(len(fs))])
def freq(x, t0, t1):
    s = seg(x, t0, t1); i = np.where((s[:-1] < 0) & (s[1:] >= 0))[0]
    if len(i) < 2: return 0.0
    z = i + s[i] / (s[i] - s[i + 1]); return (len(z) - 1) / ((z[-1] - z[0]) / SR)
def freq_ph(x, f0, t0, t1):
    """frecuencia por la fase (pasa-banda alrededor de f0 + Hilbert): no la engañan clics ni ruido"""
    b = sg.sosfiltfilt(sg.butter(4, [f0 * 0.8, f0 * 1.2], "bp", fs=SR, output="sos"), x)
    ph = np.unwrap(np.angle(sg.hilbert(b))); return (ph[I(t1)] - ph[I(t0)]) / (2 * np.pi) / (t1 - t0)
def env(x):
    e = np.abs(sg.hilbert(x)); k = int(0.002 * SR); return np.convolve(e, np.ones(k) / k, "same")
def rms(x, t0, t1): return db(np.sqrt(np.mean(seg(x, t0, t1) ** 2)))
def last_sound(x, thr=1e-5):
    i = np.where(np.abs(x) > thr)[0]; return i[-1] / SR if len(i) else 0.0
def clicks(x, thr):
    """tiempos de los clics: picos de la envolvente de los agudos (> 3 kHz)"""
    h = sg.sosfilt(sg.butter(4, 3000, "hp", fs=SR, output="sos"), x)
    e = np.convolve(np.abs(h), np.ones(48) / 48, "same")
    pk, _ = sg.find_peaks(e, height=thr, distance=int(0.2 * SR)); return pk / SR

fails = 0
def scalar(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:52s} {got:+11.4f}   (esperado {want:+.4f} ± {tol})")
def inrange(name, got, lo, hi):
    global fails
    ok = lo <= got <= hi; fails += not ok
    print(f"{'OK ' if ok else 'MAL'} {name:52s} {got:+11.4f}   (entre {lo:+.3f} y {hi:+.3f})")

LOG = {}
for l in (D / "log.txt").read_text().splitlines():
    m = re.match(r"caso (\S+) \| frames (\S+) \| chops (\S+) \| nota (\S+)", l)
    if m: LOG[m.group(1)] = dict(frames=float(m.group(2)), chops=float(m.group(3)), nota=float(m.group(4)))

for p in sorted(D.glob("*.wav")):
    if p.stem.startswith(("perf_", "smoke")): continue
    x = load(p.stem)
    if not np.all(np.isfinite(x)) or np.abs(x).max() > 2:
        fails += 1; print("MAL", p.stem, "tiene NaN o pasa de +6 dBFS")

print("--- lectura del sample")
x = load("null_noise"); s = src("noise_st")
scalar("nulo a la nota raiz: max |salida - sample| (24 bit)", np.abs(x[I(0.1):I(0.1) + 48000] - s).max(), 0, 2e-7)
inrange("nulo: silencio despues del sample (dB)", rms(x, 1.11, 1.45), -400, -120)
x = load("onset"); scalar("la nota empieza exacto en su muestra (0.5 s)", np.where(np.abs(x[:, 0]) > 0)[0][0], 24000, 0)
x = load("srconv")[:, 0]
scalar("sample a 44.1 kHz: 220 Hz en proyecto a 48 kHz", freq(x, 0.2, 1.0), 220, 0.01)
scalar("sample a 44.1 kHz: nivel", tone(x, 220, 0.2, 1.0), db(0.5), 0.02)
scalar("sample a 44.1 kHz: dura 1.0 s", last_sound(x, 1e-3), 1.1, 0.002)
scalar("teclado: +12 st = 880 Hz", freq(load("kt_oct")[:, 0], 0.3, 1.4), 880, 0.02)
scalar("teclado: +7 st = 659.26 Hz", freq(load("kt_fifth")[:, 0], 0.3, 1.4), mtof(76), 0.02)
scalar("tono fijo: C5 suena igual (440 Hz)", freq(load("kt_off")[:, 0], 0.3, 1.4), 440, 0.01)
scalar("nota raiz A4: A4 suena tal cual", freq(load("root")[:, 0], 0.3, 1.4), 440, 0.01)
scalar("tono -12 st = 220 Hz", freq(load("tono")[:, 0], 0.3, 1.4), 220, 0.01)
scalar("fino +50 c = 452.89 Hz", freq(load("fino")[:, 0], 0.3, 1.4), 440 * 2 ** (50 / 1200), 0.02)
x = load("startend")[:, 0]; o = I(0.1)
scalar("inicio 25 %: primer valor = rampa(12000)", x[o], 0.9 * 12000 / 48000, 1e-6)
scalar("inicio 25 %: valor 1000 muestras despues", x[o + 1000], 0.9 * 13000 / 48000, 1e-6)
scalar("fin 50 %: ultimo valor = rampa(23999)", x[o + 11999], 0.9 * 23999 / 48000, 1e-6)
inrange("fin 50 %: silencio despues", np.abs(x[o + 12000:]).max(), 0, 1e-9)
x = load("reverse")[:, 0]
scalar("reverso: primer valor = rampa(47999)", x[o], 0.9 * 47999 / 48000, 1e-6)
scalar("reverso: a los 0.5 s = rampa(23999)", x[o + 24000], 0.9 * 23999 / 48000, 1e-6)

print("--- loops")
x = load("loop_fwd")[:, 0]
scalar("loop adelante: sigue sonando a 440 Hz (3-4 s)", freq(x, 3.0, 4.0), 440, 0.01)
w = [rms(x, t, t + 0.05) for t in np.arange(0.2, 4.0, 0.05)]
inrange("loop adelante (periodos enteros): nivel parejo (dB)", max(w) - min(w), 0, 0.05)
def spike(name):
    h = sg.sosfilt(sg.butter(4, 4000, "hp", fs=SR, output="sos"), load(name)[:, 0]); return np.abs(seg(h, 1.2, 3.0)).max()
a, b = spike("loop_noxf"), spike("loop_xf")
inrange("loop sin crossfade: el salto hace clic (agudos)", a, 0.01, 10)
inrange("crossfade 30 ms: el clic baja (dB)", db(b / a), -100, -20)
x = load("pingpong")[:, 0]
scalar("ping-pong: en 1.5 s vuelve al inicio del loop (0.18)", x[I(1.5)], 0.18, 0.002)
scalar("ping-pong: en 2.1 s llega al fin del loop (0.72)", x[I(2.1)], 0.72, 0.002)
inrange("ping-pong: minimo entre 1 y 3 s", seg(x, 1.0, 3.0).min(), 0.178, 0.182)
inrange("ping-pong: maximo entre 1 y 3 s", seg(x, 1.0, 3.0).max(), 0.718, 0.722)

print("--- disparo, fades, velocidad y envolvente")
x = load("oneshot")[:, 0]
scalar("one-shot: suena hasta el final (2.1 s) aunque la nota dure 50 ms", last_sound(x, 1e-3), 2.1, 0.002)
inrange("mantener: se apaga al soltar (0.3-2 s, dB)", rms(load("gate")[:, 0], 0.3, 2.0), -400, -90)
x = load("fades")[:, 0]; e = env(x)
scalar("fade in 100 ms: a los 50 ms va por la mitad", e[I(0.15)], 0.25, 0.005)
scalar("fade in: a los 500 ms, completo", e[I(0.6)], 0.5, 0.003)
scalar("fade out 200 ms: 100 ms antes del fin va por la mitad", e[I(1.0)], 0.25, 0.005)
scalar("velocidad 100 %: vel 64 = (64/127)^2", tone(load("vel")[:, 0], 440, 0.9, 1.25) - tone(load("vel")[:, 0], 440, 0.2, 0.55), 40 * np.log10(64 / 127), 0.03)
scalar("velocidad 0 %: vel 64 suena igual", tone(load("vel0")[:, 0], 440, 0.9, 1.25) - tone(load("vel0")[:, 0], 440, 0.2, 0.55), 0, 0.01)
e = env(load("env_a")[:, 0])
scalar("ataque 100 ms: a los 50 ms = mitad", e[I(0.15)], 0.25, 0.005)
scalar("ataque 100 ms: a los 200 ms = completo", e[I(0.3)], 0.5, 0.003)
e = env(load("env_ds")[:, 0])
scalar("decaimiento 200 ms a sostenido 50 %: a los 600 ms", e[I(0.7)], 0.25, 0.003)
e = env(load("env_r")[:, 0])
scalar("relajacion 300 ms: -40 dB a los 300 ms", db(e[I(0.8)] / e[I(0.45)]), -40, 1.0)

print("--- filtro (curva bilineal del SVF, armonico por armonico)")
f0 = mtof(60); off = load("flt_off")[:, 0]
def fstage(w, k, t): d = np.sqrt((1 - w * w) ** 2 + (k * w) ** 2); return 1 / d if t == 0 else k * w / d if t == 1 else w * w / d
def theo(f, fc, typ, reso=0):
    w = np.tan(np.pi * f / SR) / np.tan(np.pi * fc / SR); k = np.sqrt(2) * (1 - 0.985 * reso / 100)
    return [fstage(w, np.sqrt(2), 0) * fstage(w, k, 0), fstage(w, k, 0), fstage(w, k, 1), fstage(w, k, 2)][typ]
H12 = [k * f0 for k in range(1, 40) if k * f0 < 20000]; base = tones(off, H12, 0.3, 1.0)
for name, typ, reso in (("flt_lp24", 0, 0), ("flt_lp12", 1, 0), ("flt_bp", 2, 0), ("flt_hp", 3, 0), ("flt_reso", 1, 80)):
    got = tones(load(name)[:, 0], H12, 0.3, 1.0) - base
    errs = [g - db(theo(f, 1000, typ, reso)) for g, f in zip(got, H12) if db(theo(f, 1000, typ, reso)) > -45]
    inrange(f"{name}: error max. contra la teoria (dB, armonicos > -45 dB)", max(np.abs(errs)), 0, 0.15)
x = load("env2cut")[:, 0]
inrange("env 2 a corte: el armonico 10 empieza abierto y se cierra (dB)", tone(x, 10 * f0, 0.11, 0.16) - tone(x, 10 * f0, 0.9, 1.2), 20, 200)
x = load("drive")[:, 0]
inrange("drive 12 dB: aparece el 3er armonico (dB rel.)", tone(x, 1320, 0.3, 1.2) - tone(x, 440, 0.3, 1.2), -40, -5)
x = load("env2tono")[:, 0]
inrange("env 2 a tono +12 (decae en 100 ms): empieza sobre +8 st", freq(x, 0.1, 0.11), 700, 880)
scalar("env 2 a tono: vuelve a 440 Hz", freq(x, 0.6, 1.1), 440, 0.02)

print("--- voces")
x = load("poly")[:, 0]; F3 = [440, 440 * 2 ** (4 / 12), 440 * 2 ** (7 / 12)]
for f, g in zip(F3, tones(x, F3, 0.3, 1.4)):
    scalar(f"poly: {f:.1f} Hz al nivel de una voz (-12 dB)", g, db(0.5) - 12, 0.02)
g = tones(load("voices2")[:, 0], F3, 0.5, 1.4)
inrange("2 voces: la mas vieja (440) se apago (dB)", g[0], -400, -80)
inrange("2 voces: las otras dos suenan", min(g[1:]), db(0.5) - 0.05, db(0.5) + 0.05)
x = load("retrig")[:, 0]
inrange("misma nota otra vez: como mucho 2 voces en el fundido", np.abs(x).max(), 0.49, 1.0)
scalar("misma nota otra vez: queda una sola voz", tone(x, 440, 0.6, 0.85), db(0.5), 0.02)
x = load("mono")[:, 0]
inrange("mono: con la 2a nota no suena la 1a (dB)", tone(x, 440, 0.4, 0.75), -400, -60)
scalar("mono: suena la 2a nota", tone(x, mtof(73), 0.4, 0.75), db(0.5), 0.02)
scalar("mono: al soltarla vuelve la 1a", tone(x, 440, 1.0, 1.35), db(0.5), 0.02)
mid = 440 * 2 ** (3 / 12)    # de C3 (-3 st) a A4 (+9 st): la mitad del glide = +3 st
x = load("glide_leg")[:, 0]
scalar("legato: antes del glide (nota 57)", freq(x, 0.3, 0.58), 440 * 2 ** (-3 / 12), 0.03)
inrange("legato glide 200 ms: a los 100 ms va por la mitad (Hz)", freq(x, 0.695, 0.705), mid - 6, mid + 6)
scalar("legato glide: llega a la nota 69", freq(x, 0.9, 1.25), 440 * 2 ** (9 / 12), 0.05)
inrange("mono glide: con notas separadas tambien se desliza", freq(load("glide_mono")[:, 0], 0.695, 0.705), mid - 6, mid + 6)
scalar("legato sin pisar: no hay glide", freq(load("glide_leg_sep")[:, 0], 0.62, 0.7), 440 * 2 ** (9 / 12), 0.2)
scalar("legato: la 2a nota NO reinicia el sample (sigue la rampa)", load("legato_pos")[I(0.75), 0], 0.9 * 0.65, 0.01)
scalar("mono: la 2a nota reinicia el sample", load("mono_pos")[I(0.75), 0], 0.9 * 0.15, 0.01)
scalar("pitch bend +2 st", freq(load("bend")[:, 0], 0.3, 1.2), mtof(71), 0.05)
x = load("modwheel")[:, 0]; fr = [freq(x, t, t + 0.03) for t in np.arange(0.3, 1.2, 0.01)]
inrange("rueda: vibrato de +/-40 c (Hz pico a pico)", max(fr) - min(fr), 12, 25)
x = load("pedal")[:, 0]
scalar("pedal: sigue sonando despues de soltar", rms(x, 0.4, 0.75), db(0.5 / np.sqrt(2)), 0.05)
inrange("pedal: al levantarlo se apaga", rms(x, 0.95, 1.35), -400, -80)

print("--- chops")
x = load("ch_equal")[:, 0]; o = I(0.1)
scalar("4 partes: chop 1 empieza en 0", x[o + 100], 0.9 * 100 / 48000, 1e-6)
inrange("4 partes: chop 1 dura 0.25 s (silencio 0.35-0.6)", np.abs(seg(x, 0.351, 0.599)).max(), 0, 1e-9)
scalar("4 partes: la nota 38 toca el chop 3 (rampa(24000))", x[I(0.6)], 0.45, 1e-6)
H = [0.05, 0.31, 0.52, 0.80, 1.01, 1.27, 1.55, 1.78]
scalar("transitorios: encuentra los 8 golpes", LOG["ch_trans"]["chops"], 8, 0)
x = load("ch_trans")[:, 0]; s = src("hits8")
for k in range(8):
    o = I(0.1 + 0.3 * k); y = x[o:o + 960]
    lags = np.arange(I(H[k] - 0.01), I(H[k] + 0.01))
    best = lags[np.argmax([np.dot(y, s[l:l + 960]) / (np.linalg.norm(s[l:l + 960]) + 1e-12) for l in lags])]
    inrange(f"transitorios: chop {k + 1} empieza en el golpe {H[k]:.2f} s (ms)", (best / SR - H[k]) * 1000, -2.0, 0.5)
inrange("sensibilidad 0: no encuentra mas chops que con 50", LOG["ch_sens0"]["chops"], 1, 8)
scalar("hasta el final del sample: chop 7 de 8 dura 0.25 s", last_sound(load("ch_thru")[:, 0], 1e-9) - 0.1, 0.25, 0.001)
scalar("hasta su final: chop 7 de 8 dura 0.125 s", last_sound(load("ch_nothru")[:, 0], 1e-9) - 0.1, 0.125, 0.001)
scalar("choke: el 2o chop corta al 1o", load("ch_choke")[I(0.21), 0], 0.9 * (12000 + 480) / 48000, 1e-4)
scalar("sin choke: suenan los dos", load("ch_nochoke")[I(0.21), 0], 0.9 * (12000 + 480) / 48000 + 0.9 * 0.11, 1e-4)
x = load("ch_params")[:, 0]
scalar("chop 1 sin cambios: 440 Hz", freq(x, 0.15, 0.45), 440, 0.02)
scalar("chop 2 con tono +12: 880 Hz", freq(x, 0.65, 0.95), 880, 0.03)
scalar("chop 3 con ganancia -6 dB", tone(x, 440, 1.15, 1.45), db(0.5) - 6, 0.02)
scalar("chop 2 en reverso: empieza en rampa(23999)", load("ch_rev")[I(0.1), 0], 0.9 * 23999 / 48000, 1e-6)
scalar("nota del primer chop = C4: C4 toca el chop 1", load("ch_base")[I(0.1) + 100, 0], 0.9 * 100 / 48000, 1e-6)

print("--- estirar, a tempo y calidad")
x = load("st_slow")[:, 0]
scalar("estirar 50 %: mantiene 440 Hz", freq(x, 1.0, 3.5), 440, 0.05)
w = [rms(x, t, t + 0.05) for t in np.arange(0.3, 3.8, 0.05)]
inrange("estirar 50 %: nivel parejo (dB pico a pico)", max(w) - min(w), 0, 1.0)
scalar("estirar 50 %: nivel", np.mean(w), db(0.5 / np.sqrt(2)), 0.3)
scalar("estirar 50 %: dura el doble (termina en ~4.1 s)", last_sound(x, 1e-3), 4.12, 0.06)
x = load("st_pitch")[:, 0]
scalar("estirar con +12 st: 880 Hz", freq(x, 0.5, 1.8), 880, 0.1)
scalar("estirar con +12 st: dura lo mismo (2 s)", last_sound(x, 1e-3), 2.12, 0.06)
c = clicks(load("st_loop")[:, 0], 0.02)
scalar("estirar al 100 %: clics cada 0.6 s", np.mean(np.diff(c)), 0.6, 0.004)
x = load("sync_vinyl")[:, 0]
scalar("a tempo (vinilo) 100 -> 120 BPM: tono x1.2 (360 Hz)", freq_ph(x, 360, 1.0, 3.5), 360, 0.02)
c = clicks(x, 0.02); scalar("a tempo (vinilo): clics cada 0.5 s", np.mean(np.diff(c)), 0.5, 0.003)
scalar("a tempo (vinilo): 2 compases = 4.0 s", last_sound(x, 1e-3), 4.0, 0.01)
x = load("sync_stretch")[:, 0]
scalar("a tempo (estirar): el tono no cambia (300 Hz)", freq_ph(x, 300, 1.0, 3.5), 300, 0.02)
c = clicks(x, 0.02); scalar("a tempo (estirar): clics cada 0.5 s", np.mean(np.diff(c)), 0.5, 0.004)
an, aa = tone(load("q_normal")[:, 0], 18000, 0.15, 0.55), tone(load("q_alta")[:, 0], 18000, 0.15, 0.55)
inrange("calidad Normal: 15 kHz +12 st deja alias en 18 kHz (dB)", an, -60, 0)
inrange("calidad Alta: el alias queda bajo -85 dB", aa, -400, -85)
scalar("calidad Alta: 5 kHz +12 st = 10 kHz sin perder nivel", tone(load("q_alta_pass")[:, 0], 10000, 0.15, 0.55), db(0.5), 0.2)
scalar("calidad Alta: 5 kHz -12 st = 2.5 kHz sin perder nivel", tone(load("q_alta_down")[:, 0], 2500, 0.2, 0.8), db(0.5), 0.1)

print("--- salida")
scalar("normalizar: pico del sample a 0 dB", tone(load("normalize")[:, 0], 440, 0.2, 1.0), 0, 0.02)
scalar("sin normalizar: -12 dB", tone(load("nonorm")[:, 0], 440, 0.2, 1.0), db(0.25), 0.02)
x = load("pan")
scalar("paneo +50 %: izquierda -6 dB", tone(x[:, 0], 440, 0.2, 1.0), db(0.25), 0.02)
scalar("paneo +50 %: derecha igual", tone(x[:, 1], 440, 0.2, 1.0), db(0.5), 0.02)
x = load("width0"); inrange("ancho 0 %: L = R", np.abs(x[:, 0] - x[:, 1]).max(), 0, 1e-6)
x = load("width200"); s = src("noise_st"); y = x[I(0.1):I(0.1) + 48000]
scalar("ancho 200 %: el lado (L-R) se duplica (dB)", db(np.std(y[:, 0] - y[:, 1]) / np.std(s[:, 0] - s[:, 1])), db(2), 0.01)
scalar("volumen -6 dB", tone(load("volume")[:, 0], 440, 0.2, 1.0), db(0.5) - 6, 0.02)
x = seg(load("bits4")[:, 0], 0.2, 1.0)
inrange("4 bits: todo es multiplo de 1/8", np.abs(x * 8 - np.round(x * 8)).max(), 0, 1e-5)
x = seg(load("srred")[:, 0], 0.2, 1.0)
scalar("muestreo 6 kHz: la salida se repite 8 muestras (7/8 sin cambio)", np.mean(np.diff(x) == 0), 7 / 8, 0.01)
e = env(load("lfo_vol")[:, 0]); s = seg(e, 0.3, 1.2)
inrange("LFO a volumen 100 %: el tremolo llega casi a 0", s.min() / s.max(), 0, 0.05)
pk, _ = sg.find_peaks(s, distance=int(0.15 * SR)); scalar("LFO a volumen: 4 Hz", SR / np.mean(np.diff(pk)), 4, 0.05)
x = load("lfo_pan"); el, er = env(x[:, 0]), env(x[:, 1])
inrange("LFO a paneo: L y R se turnan (correlacion)", np.corrcoef(seg(el, 0.3, 1.2), seg(er, 0.3, 1.2))[0, 1], -1, -0.5)
inrange("LFO a paneo: cada lado llega casi a 0", max(seg(el, 0.3, 1.2).min(), seg(er, 0.3, 1.2).min()) / 0.5, 0, 0.05)
x = load("lfo_pitch")[:, 0]; fr = [freq(x, t, t + 0.02) for t in np.arange(0.3, 1.2, 0.01)]
inrange("LFO a tono 10 % (+/-1.2 st): Hz pico a pico", max(fr) - min(fr), 45, 70)

print("--- deteccion de nota, proyecto guardado")
scalar("nota detectada: seno +30 c = 69.30", LOG["det_off30"]["nota"], 69.30, 0.02)
scalar("nota detectada: sierra C4 = 60.00", LOG["det_saw"]["nota"], 60.00, 0.02)
scalar("nota detectada: 220 Hz a 44.1 kHz = 57.00", LOG["det_44k"]["nota"], 57.00, 0.02)
a = load("reopen_a")
inrange("guardar y reabrir: suena igual", np.abs(load("reopen_b") - a).max(), 0, 1e-7)
inrange("audio guardado en el proyecto: suena igual sin el archivo", np.abs(load("embed") - a).max(), 0, 1e-7)
inrange("sin guardarlo y sin el archivo: ya no suena igual", np.abs(load("noembed") - a).max(), 1e-3, 10)

print("--- presets y estres")
for p in sorted(D.glob("preset*.wav"), key=lambda q: int(q.stem[6:])):
    x = load(p.stem); inrange(f"{p.stem}: suena (pico dBFS)", db(np.abs(x).max()), -30, 0.5)
for n in ("stress", "stress_st"):
    inrange(f"{n}: pico dBFS", db(np.abs(load(n)).max()), -40, 6)

print("FALLAS:", fails)
sys.exit(1 if fails else 0)
