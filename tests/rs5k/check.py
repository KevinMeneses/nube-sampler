"""Compara tests/out/rs5k_orig.wav (17 RS5k) con rs5k_nube.wav (Nube Sampler en zonas) nota por nota (47..68, velocidad
100 y 76), y rs5k_nube_emb.wav (reabierto con el audio guardado en el proyecto, sin la carpeta) con rs5k_nube.wav."""
import numpy as np, soundfile as sf, pathlib, sys
D = pathlib.Path(__file__).parent.parent / "out"
NOTE, GAP = 1.2, 0.6
o, sr = sf.read(D / "rs5k_orig.wav"); n, sr2 = sf.read(D / "rs5k_nube.wav"); e, sr3 = sf.read(D / "rs5k_nube_emb.wav")
assert sr == sr2 == sr3 == 48000
L = min(len(o), len(n), len(e)); o, n, e = o[:L], n[:L], e[:L]
def db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
BANDS = [(60, 250), (250, 1000), (1000, 4000), (4000, 12000)]   # solo cuentan las que están a menos de 30 dB de la más fuerte
def bands(x):
    X = np.abs(np.fft.rfft(x.mean(1) * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1 / sr)
    return np.array([10 * np.log10(X[(f >= a) & (f < b)].sum() + 1e-20) for a, b in BANDS])
fails = 0; rows = []
t = 0.0
for vel in (100, 76):
    for p in range(47, 69):
        a, b = int(t * sr), int((t + NOTE + GAP) * sr)
        so, sn = o[a:b], n[a:b]
        lv = db(sn) - db(so)
        bo, bn = bands(so), bands(sn); keep = bo > bo.max() - 30
        bd = np.max(np.abs(bn - bo)[keep])
        c = np.sum(so * sn) / np.sqrt(np.sum(so ** 2) * np.sum(sn ** 2))
        res = db(sn - so) - db(so)
        rows.append((p, vel, lv, bd, c, res))
        ok = abs(lv) <= 0.25 and bd <= 0.5 and c >= 0.999 and res <= -30
        fails += not ok
        t += NOTE + GAP
print(" nota vel   nivel   bandas  forma  residuo")
for p, vel, lv, bd, c, res in rows:
    print(f"  {p:3d} {vel:3d}  {lv:+.2f}   {bd:5.2f}   {c:.4f}  {res:6.1f} dB" + ("" if abs(lv) <= 0.25 and bd <= 0.5 and c >= 0.999 and res <= -30 else "   <-- FALLA"))
r = np.array([x[2:] for x in rows])
print(f"resumen: nivel {r[:,0].min():+.2f}..{r[:,0].max():+.2f} dB | bandas máx {r[:,1].max():.2f} dB | forma de onda min {r[:,2].min():.4f}"
      f" | residuo mediana {np.median(r[:,3]):.1f} dB")
de = np.max(np.abs(e - n))
print(f"reabierto con el audio en el proyecto: diferencia máx {de:.2e}" + ("" if de < 1e-6 else "   <-- FALLA"))
fails += de >= 1e-6
print("OK" if not fails else f"{fails} FALLAS"); sys.exit(1 if fails else 0)
