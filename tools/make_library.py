"""Genera la biblioteca de fábrica de Nube Sampler en samples/Nube (48 kHz, 24 bit). Todo sintetizado aquí: sin
grabaciones de terceros. Uso: python3 tools/make_library.py  (necesita numpy y soundfile)."""
import numpy as np, soundfile as sf, pathlib
from numpy.random import default_rng
SR = 48000
OUT = pathlib.Path(__file__).resolve().parent.parent / "samples/Nube"
rng = default_rng(7)


def mtof(n): return 440 * 2 ** ((n - 69) / 12)
def t_(d): return np.arange(int(d * SR)) / SR
def norm(x, pk=0.89): return x / np.max(np.abs(x)) * pk
def st(l, r=None): return np.stack([l, l if r is None else r], 1)
def lp1(x, fc):
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * fc / SR); return lfilter([1 - a], [1, -a], x)
def lpf(x, fc, n=2):
    for _ in range(n): x = lp1(x, fc)
    return x
def save(name, x): OUT.mkdir(parents=True, exist_ok=True); sf.write(OUT / f"{name}.wav", x, SR, subtype="PCM_24")


def rhodes(n, dur=3.0, vel=1.0):
    t = t_(dur); f = mtof(n)
    idx = 1.8 * vel * np.exp(-t * 3.5) + 0.25
    car = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    tine = 0.25 * vel * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 40)
    env = np.exp(-t * 1.2) * (1 - np.exp(-t * 900))
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.2 * t)
    x = (car + tine) * env
    return st(x * trem, x * (2 - trem))


def e808(n=36, dur=2.6):
    t = t_(dur); f = mtof(n)
    fr = f * (1 + 1.2 * np.exp(-t * 28))
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 1.1) * (1 - np.exp(-t * 2000))
    return st(np.tanh(2.2 * x) / np.tanh(2.2))


def kick():
    t = t_(0.6); fr = 48 + 140 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7)
    click = lpf(rng.standard_normal(len(t)), 3000) * np.exp(-t * 300) * 0.6
    return st(np.tanh(1.5 * (x + click)))


def snare():
    t = t_(0.45)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 22) * 0.7
    nz = rng.standard_normal(len(t)); nz = nz - lpf(nz, 1200)
    return st(body + nz * np.exp(-t * 13) * 0.6)


def hat(dur, dec):
    t = t_(dur); nz = rng.standard_normal(len(t)); nz = nz - lpf(nz, 7000, 3)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (317, 421, 563, 739, 819, 1031)) / 6
    m = metal - lpf(metal, 7000, 3)
    return st((nz * 0.7 + m * 0.6) * np.exp(-t * dec))


def clap():
    t = t_(0.5); nz = rng.standard_normal(len(t)); nz = lpf(nz - lpf(nz, 900), 5000)
    env = np.zeros_like(t)
    for k, d in enumerate((0, 0.011, 0.022, 0.034)):
        env += (t >= d) * np.exp(-np.maximum(t - d, 0) * (180 if k < 3 else 16))
    return st(nz * env)


def rim():
    t = t_(0.15)
    return st((np.sin(2 * np.pi * 1700 * t) * 0.6 + np.sin(2 * np.pi * 820 * t)) * np.exp(-t * 60))


def vocal_aah(n=60, dur=3.0):
    from scipy.signal import lfilter
    t = t_(dur); f0 = mtof(n) * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t - 0.4, 0, 1))
    ph = np.cumsum(f0) / SR
    src = np.zeros_like(t); h = 1
    while h * mtof(n) < 9000:
        src += np.sin(2 * np.pi * h * ph) / h ** 1.1; h += 1
    y = np.zeros_like(t)
    for fc, bw, g in ((800, 80, 1.0), (1150, 90, 0.6), (2900, 120, 0.25), (3300, 150, 0.15)):
        r = np.exp(-np.pi * bw / SR); th = 2 * np.pi * fc / SR
        z = lfilter([1], [1, -2 * r * np.cos(th), r * r], src)
        y += g * z / np.max(np.abs(z))
    env = np.minimum(1, t / 0.12) * np.minimum(1, (dur - t) / 0.4)
    return st(y * env + 0.004 * rng.standard_normal(len(t)) * env)


def pad(n=48, dur=4.0):
    t = t_(dur); l = np.zeros_like(t); r = np.zeros_like(t)
    for k, c in enumerate(np.linspace(-14, 14, 7)):
        f = mtof(n) * 2 ** (c / 1200); saw = 2 * ((f * t + rng.random()) % 1) - 1
        pl = 0.15 + 0.7 * k / 6
        l += saw * (1 - pl); r += saw * pl
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.8)
    return st(lpf(l, 1800) * env, lpf(r, 1800) * env)


def ks(f, dur, damp=0.996):
    n = int(dur * SR); p = int(SR / f); buf = lpf(rng.uniform(-1, 1, p), 5000, 1).tolist()
    y = np.zeros(n)
    for i in range(n):
        j = i % p; y[i] = buf[j]; buf[j] = damp * 0.5 * (buf[j] + buf[(j + 1) % p])
    return y


def guitar_arp(bpm=90):
    beat = 60 / bpm; dur = 8 * beat; y = np.zeros(int(dur * SR))
    notes = [57, 64, 67, 72, 53, 60, 65, 69, 48, 55, 64, 67, 55, 62, 67, 71]
    for k, nn in enumerate(notes):
        s = int(k * beat / 2 * SR); g = ks(mtof(nn), 1.6) * (0.9 if k % 4 == 0 else 0.6)
        e = min(len(y), s + len(g)); y[s:e] += g[:e - s]
    return st(y)


def chill_loop(bpm=90, bars=4):
    beat = 60 / bpm; n = int(round(bars * 4 * beat * SR)); L = np.zeros(n); R = np.zeros(n)
    def put(x, t0, g=1.0):
        s = int(round(t0 * SR)); e = min(n, s + len(x)); L[s:e] += x[:e - s, 0] * g; R[s:e] += x[:e - s, 1] * g
    K, S, H = kick(), snare(), hat(0.08, 60)
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]
    for b in range(bars):
        t0 = b * 4 * beat
        for nn in chords[b % 4]: put(rhodes(nn, 4 * beat, 0.6) * 0.18, t0)
        put(e808(chords[b % 4][0] - 12, 4 * beat) * 0.35, t0)
        put(K, t0, 0.8); put(K, t0 + 2.5 * beat, 0.6); put(S, t0 + beat, 0.55); put(S, t0 + 3 * beat, 0.55)
        for k in range(8): put(H, t0 + k * beat / 2, 0.25 if k % 2 else 0.35)
    return np.stack([L, R], 1)


def vinyl(dur=4.0):
    t = t_(dur); hiss = lpf(rng.standard_normal(len(t)), 5000) * 0.03
    cr = np.zeros_like(t); idx = rng.integers(0, len(t), 160); cr[idx] = rng.uniform(-1, 1, 160)
    x = hiss + (cr - lpf(cr, 1500)) * 0.5 + 0.01 * np.sin(2 * np.pi * 60 * t)
    fade = int(0.05 * SR); x[:fade] *= np.linspace(0, 1, fade); x[-fade:] *= np.linspace(1, 0, fade)
    return st(x, np.roll(x, 300))


def kalimba(n=72, dur=2.0):
    t = t_(dur); f = mtof(n)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 30)
    return st(x * (1 - np.exp(-t * 3000)))


if __name__ == "__main__":
    lib = {
        "Keys - Rhodes C4": rhodes(60), "Bajo - 808 C2": e808(36), "Bateria - Kick": kick(), "Bateria - Snare": snare(),
        "Bateria - Hat cerrado": hat(0.12, 45), "Bateria - Hat abierto": hat(0.6, 7), "Bateria - Clap": clap(),
        "Bateria - Rim": rim(), "Vocal - Aah C4": vocal_aah(60), "Pad - Nube C3": pad(48),
        "Guitarra - Arpegio 90 BPM 2 compases": guitar_arp(90), "Loop - Chill 90 BPM 4 compases": chill_loop(90, 4),
        "Textura - Vinilo": vinyl(), "Kalimba C5": kalimba(72),
    }
    for k, v in lib.items():
        save(k, norm(v)); print("ok", k, f"{len(v) / SR:.2f} s")
