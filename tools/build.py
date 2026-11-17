"""Genera nube_sampler.jsfx desde src/nube_sampler.template.jsfx y tests/params_gen.lua.
La tabla SPEC es la única fuente de los parámetros: sliders, sset(), tabla de la interfaz y valores por defecto.
El slider 1 es el archivo (biblioteca en REAPER/Data/Nube Sampler); SPEC empieza en el slider 2.
Marcadores en el template: //@GEN:<NOMBRE>@ en una línea propia."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "src/nube_sampler.template.jsfx", ROOT / "nube_sampler.jsfx"

FIGS = "Apagado,1/32,1/16T,1/16,1/8T,1/16.,1/8,1/4T,1/8.,1/4,1/2T,1/4.,1/2,1/2.,1/1,2/1,4/1"
SYNC = "Apagado,1 tiempo,2 tiempos,1 compas,2 compases,4 compases,8 compases,16 compases"
FILE_SLIDER = "slider1:/Nube Sampler:Nube/Keys - Rhodes C4.wav:Sample"
# unidades para la interfaz: 0 entero, 1 %, 2 Hz, 3 ms, 4 st, 5 cents, 6 dB, 7 s, 8 lista, 9 nota
# curva de la perilla: 0 lineal, 1 log, 2 cuadrática, 3 cúbica
# (nombre, defecto, mín, máx, paso, log_mid o None, lista o None, unidad, curva)
SPEC = [
    ("Modo", 0, 0, 1, 1, None, "Clasico,Chops", 8, 0),                                   # 2
    ("Disparo", 0, 0, 1, 1, None, "Mantener,One-shot", 8, 0),                             # 3
    ("Reproduccion", 0, 0, 1, 1, None, "Remuestreo,Estirar", 8, 0),                       # 4
    ("Inicio (%)", 0, 0, 100, 0.001, None, None, 1, 0),                                   # 5
    ("Fin (%)", 100, 0, 100, 0.001, None, None, 1, 0),                                    # 6
    ("Reverso", 0, 0, 1, 1, None, "No,Si", 8, 0),                                         # 7
    ("Loop", 0, 0, 2, 1, None, "Apagado,Adelante,Ping-pong", 8, 0),                       # 8
    ("Loop inicio (%)", 0, 0, 100, 0.001, None, None, 1, 0),                              # 9
    ("Loop fin (%)", 100, 0, 100, 0.001, None, None, 1, 0),                               # 10
    ("Crossfade del loop (ms)", 10, 0, 500, 0.1, None, None, 3, 2),                       # 11
    ("Fade in (ms)", 0, 0, 2000, 0.1, None, None, 3, 3),                                  # 12
    ("Fade out (ms)", 0, 0, 5000, 0.1, None, None, 3, 3),                                 # 13
    ("Nota raiz", 60, 0, 127, 1, None, None, 9, 0),                                       # 14
    ("Seguir teclado", 1, 0, 1, 1, None, "No,Si", 8, 0),                                  # 15
    ("Tono (st)", 0, -24, 24, 1, None, None, 4, 0),                                       # 16
    ("Fino (cents)", 0, -100, 100, 0.1, None, None, 5, 0),                                # 17
    ("Velocidad (%)", 100, 10, 400, 0.1, 100, None, 1, 1),                                # 18
    ("A tempo", 0, 0, 7, 1, None, SYNC, 8, 0),                                            # 19
    ("Grano (ms)", 50, 10, 200, 0.1, 50, None, 3, 1),                                     # 20
    ("Calidad", 0, 0, 1, 1, None, "Normal,Alta", 8, 0),                                   # 21
    ("Chops deteccion", 0, 0, 2, 1, None, "Transitorios,Partes iguales,A mano", 8, 0),    # 22
    ("Sensibilidad (%)", 50, 0, 100, 0.1, None, None, 1, 0),                              # 23
    ("Partes", 8, 2, 32, 1, None, None, 0, 0),                                            # 24
    ("Nota del primer chop", 36, 0, 127, 1, None, None, 9, 0),                            # 25
    ("Chop suena hasta", 0, 0, 1, 1, None, "Su final,El final del sample", 8, 0),         # 26
    ("Chops a la vez", 0, 0, 1, 1, None, "Varios,Uno (choke)", 8, 0),                     # 27
    ("Modo de voces", 0, 0, 2, 1, None, "Poly,Mono,Legato", 8, 0),                        # 28
    ("Voces", 16, 1, 16, 1, None, None, 0, 0),                                            # 29
    ("Glide (ms)", 0, 0, 2000, 1, None, None, 3, 2),                                      # 30
    ("Pitch bend (st)", 2, 0, 24, 1, None, None, 4, 0),                                   # 31
    ("Rueda a vibrato (cents)", 40, 0, 100, 0.1, None, None, 5, 0),                       # 32
    ("Amp ataque (ms)", 0, 0, 10000, 0.1, None, None, 3, 3),                              # 33
    ("Amp decaimiento (ms)", 600, 1, 20000, 1, 600, None, 3, 1),                          # 34
    ("Amp sostenido (%)", 100, 0, 100, 0.1, None, None, 1, 0),                            # 35
    ("Amp relajacion (ms)", 40, 1, 20000, 1, 600, None, 3, 1),                            # 36
    ("Velocidad a volumen (%)", 50, 0, 100, 0.1, None, None, 1, 0),                       # 37
    ("Filtro", 4, 0, 4, 1, None, "Pasa-bajos 24,Pasa-bajos 12,Pasa-banda,Pasa-altos 12,Apagado", 8, 0),  # 38
    ("Corte (Hz)", 8000, 20, 20000, 1, 1000, None, 2, 1),                                 # 39
    ("Resonancia (%)", 0, 0, 100, 0.1, None, None, 1, 0),                                 # 40
    ("Drive del filtro (dB)", 0, 0, 24, 0.1, None, None, 6, 0),                           # 41
    ("Env 2 a corte (%)", 0, -100, 100, 0.1, None, None, 1, 0),                           # 42
    ("Env 2 ataque (ms)", 0, 0, 10000, 0.1, None, None, 3, 3),                            # 43
    ("Env 2 decaimiento (ms)", 400, 1, 20000, 1, 600, None, 3, 1),                        # 44
    ("Env 2 sostenido (%)", 0, 0, 100, 0.1, None, None, 1, 0),                            # 45
    ("Env 2 relajacion (ms)", 300, 1, 20000, 1, 600, None, 3, 1),                         # 46
    ("Env 2 a tono (st)", 0, -48, 48, 0.1, None, None, 4, 0),                             # 47
    ("Seguimiento de teclado (%)", 0, 0, 100, 0.1, None, None, 1, 0),                     # 48
    ("Velocidad a corte (%)", 0, 0, 100, 0.1, None, None, 1, 0),                          # 49
    ("LFO forma", 0, 0, 4, 1, None, "Seno,Triangulo,Sierra,Cuadrada,Aleatorio", 8, 0),    # 50
    ("LFO velocidad (Hz)", 4, 0.05, 20, 0.01, 2, None, 2, 1),                            # 51
    ("LFO a tempo", 0, 0, 16, 1, None, FIGS, 8, 0),                                       # 52
    ("LFO destino", 0, 0, 3, 1, None, "Tono,Corte,Volumen,Paneo", 8, 0),                  # 53
    ("LFO cantidad (%)", 0, -100, 100, 0.1, None, None, 1, 0),                            # 54
    ("LFO reinicio", 0, 0, 1, 1, None, "Libre,Con cada nota", 8, 0),                      # 55
    ("Lo-fi bits", 24, 4, 24, 1, None, None, 0, 0),                                       # 56
    ("Lo-fi muestreo (Hz)", 48000, 1000, 48000, 1, 12000, None, 2, 1),                   # 57
    ("Paneo (%)", 0, -100, 100, 0.1, None, None, 1, 0),                                   # 58
    ("Ancho estereo (%)", 100, 0, 200, 0.1, None, None, 1, 0),                            # 59
    ("Volumen (dB)", 0, -24, 12, 0.1, None, None, 6, 0),                                  # 60
    ("Normalizar", 0, 0, 1, 1, None, "No,Si", 8, 0),                                      # 61
    ("Guardar audio en el proyecto", 0, 0, 1, 1, None, "No,Si", 8, 0),                    # 62
]
MAXCH = 32
CHOP0 = 2 + len(SPEC)                      # primer slider por chop: tono, ganancia, reverso (3 por chop)
for k in range(MAXCH):
    SPEC += [(f"Chop {k + 1} tono (st)", 0, -24, 24, 1, None, None, 4, 0),
             (f"Chop {k + 1} ganancia (dB)", 0, -24, 12, 0.1, None, None, 6, 0),
             (f"Chop {k + 1} reverso", 0, 0, 1, 1, None, "No,Si", 8, 0)]
N = 1 + len(SPEC)                          # último slider de parámetros
PRESET_SLIDER = N + 1
READOUTS = [("Notas sonando (lectura)", 0, 64, 1), ("Largo del sample (lectura, frames)", 0, 20000000, 1),
            ("Chops (lectura)", 0, 32, 1), ("Nota detectada (lectura)", -1, 128, 0.01)]
RD0 = PRESET_SLIDER + 1


def presets_enum():
    txt = SRC.read_text().split("function preset_name", 1)[1].split("function load_preset", 1)[0]
    names = re.findall(r'^\s*n == (\d+) \? "([^"]+)"', txt, re.M)
    for _, nm in names:
        assert not re.search(r"[<>,{}]", nm), f"nombre de preset con caracter prohibido: {nm}"
    return [nm for _, nm in sorted(names, key=lambda t: int(t[0]))]


def num(x):
    return f"{x:g}"


def sliders():
    out = [FILE_SLIDER]
    for i, (name, d, mn, mx, st, lm, en, _, _) in enumerate(SPEC, 2):
        shape = f":log={num(lm)}" if lm else ""
        enum = "{" + en + "}" if en else ""
        assert ">" not in (en or ""), name
        out.append(f"slider{i}:{num(d)}<{num(mn)},{num(mx)},{num(st)}{shape}{enum}>-{name}")
    pn = presets_enum()
    out.append(f"slider{PRESET_SLIDER}:0<0,{len(pn)},1{{-,{','.join(pn)}}}>-Cargar preset")
    for k, (name, mn, mx, st) in enumerate(READOUTS):
        out.append(f"slider{RD0 + k}:{num(mn if mn > 0 else 0)}<{num(mn)},{num(mx)},{num(st)}>-{name}")
    return "\n".join(out)


def sset():
    def tree(lo, hi):
        if lo == hi:
            return f"( slider{lo} = v; slider_automate(slider{lo}); )"
        mid = (lo + hi) // 2
        return f"i <= {mid} ? {tree(lo, mid)} : {tree(mid + 1, hi)}"
    return f"function sset(i, v)\n(\n  {tree(2, PRESET_SLIDER)};\n);"


def ptable():
    out = ["function ptable_init()", "("]
    for i, (_, d, mn, mx, st, lm, en, un, cu) in enumerate(SPEC, 2):
        out.append(f"  PMIN[{i}] = {num(mn)}; PMAX[{i}] = {num(mx)}; PDEF[{i}] = {num(d)}; PSTEP[{i}] = {num(st)}; PUNIT[{i}] = {un}; PCUR[{i}] = {cu};")
    out += [");"]
    return "\n".join(out)


def defaults():
    body = "\n  ".join(" ".join(f"sset({i}, {num(d)});" for i, (_, d, *_r) in list(enumerate(SPEC, 2))[j:j + 12])
                       for j in range(0, len(SPEC), 12))
    return f"function load_defaults()\n(\n  {body}\n);"


def lua():
    logp = ", ".join(f"[{i}] = {{{num(mn)}, {num(mx)}, {num(lm)}}}" for i, (_, d, mn, mx, st, lm, *_r) in enumerate(SPEC, 2) if lm)
    return (f"-- generado por tools/build.py\nreturn {{ N = {N}, PRESET = {PRESET_SLIDER}, NPRESETS = {len(presets_enum())},\n"
            f"  CHOP0 = {CHOP0}, NACT = {RD0}, FRAMES = {RD0 + 1}, NCHOPS = {RD0 + 2}, DETECT = {RD0 + 3},\n"
            f"  LOGP = {{{logp}}} }}\n")


def main():
    gen = {"SLIDERS": sliders(), "SSET": sset(), "PTABLE": ptable(), "DEFAULTS": defaults(),
           "CONSTS": (f"NPARAMS = {N}; PRESET_SLIDER = {PRESET_SLIDER}; NPRESETS = {len(presets_enum())}; "
                      f"CHOP0 = {CHOP0}; MAXCH = {MAXCH}; RD0 = {RD0};")}
    out = []
    for line in SRC.read_text().splitlines():
        s = line.strip()
        if s.startswith("//@GEN:") and s.endswith("@"):
            out.append(gen[s[7:-1]])
        else:
            out.append(line)
    txt = "\n".join(out) + "\n"
    # el template usa nombres simbólicos para los sliders de lectura y por chop
    txt = txt.replace("slider_NACT", f"slider{RD0}").replace("slider_FRAMES", f"slider{RD0 + 1}")
    txt = txt.replace("slider_NCHOPS", f"slider{RD0 + 2}").replace("slider_DETECT", f"slider{RD0 + 3}")
    txt = txt.replace("slider_PRESET", f"slider{PRESET_SLIDER}")
    DST.write_text(txt)
    (ROOT / "tests/params_gen.lua").write_text(lua())
    print(f"ok: {DST.name} ({txt.count(chr(10))} lineas, {N} sliders de parametros, {len(presets_enum())} presets)")


if __name__ == "__main__":
    main()
