"""Señales de prueba con valores conocidos (tests/samples). run.sh las copia a REAPER/Data/Nube Sampler/zz_pruebas."""
import numpy as np, soundfile as sf, pathlib
SR = 48000
D = pathlib.Path(__file__).resolve().parent / "samples"; D.mkdir(exist_ok=True)
rng = np.random.default_rng(3)
def t_(d, sr=SR): return np.arange(int(round(d * sr))) / sr
def w(name, x, sr=SR): sf.write(D / f"{name}.wav", x, sr, subtype="FLOAT")

w("noise_st", rng.uniform(-0.5, 0.5, (48000, 2)))                       # nulo: L y R distintos
w("ramp", np.arange(48000) / 48000 * 0.9)                                # posiciones: valor = 0.9 * i / N
w("sine440", 0.5 * np.sin(2 * np.pi * 440 * t_(2.0)))
w("sine220_44k", np.stack([0.5 * np.sin(2 * np.pi * 220 * t_(1.0, 44100))] * 2, 1), 44100)
w("sine_off30", 0.5 * np.sin(2 * np.pi * 440 * 2 ** (30 / 1200) * t_(1.0)))
w("sine5k", 0.5 * np.sin(2 * np.pi * 5000 * t_(1.0)))
w("sine15k", 0.5 * np.sin(2 * np.pi * 15000 * t_(1.0)))
w("quiet", 0.25 * np.sin(2 * np.pi * 440 * t_(1.0)))
f0 = 440 * 2 ** ((60 - 69) / 12); t = t_(1.0)
w("saw_c4", 0.3 * sum(np.sin(2 * np.pi * k * f0 * t) / k for k in range(1, int(20000 / f0))))
# 8 golpes en tiempos conocidos sobre un tono de fondo
HITS = [0.05, 0.31, 0.52, 0.80, 1.01, 1.27, 1.55, 1.78]; AMPS = [0.8, 0.5, 0.7, 0.35, 0.8, 0.45, 0.6, 0.4]
t = t_(2.0); x = 0.02 * np.sin(2 * np.pi * 110 * t)
for h, a in zip(HITS, AMPS):
    k = t >= h; tt = t[k] - h
    x[k] += a * (rng.uniform(-1, 1, k.sum()) * 0.6 + np.sin(2 * np.pi * 120 * tt)) * np.exp(-tt * 25)
w("hits8", x)
# loop de 2 compases a 100 BPM (4.8 s): un clic por tiempo sobre un seno de 300 Hz
t = t_(4.8); x = 0.2 * np.sin(2 * np.pi * 300 * t)
for b in range(8):
    k = (t >= b * 0.6) & (t < b * 0.6 + 0.004); x[k] += 0.7 * np.hanning(k.sum()) * rng.uniform(-1, 1, k.sum())
w("loop100", x)
print("ok", len(list(D.glob("*.wav"))), "señales")
