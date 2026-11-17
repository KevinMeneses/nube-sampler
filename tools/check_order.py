"""Dos errores de EEL2 que dejan el JSFX sin compilar (y el plugin mudo, sin aviso en los renders):
1) llamar a una función que se define más abajo: el JSFX no compila y el plugin queda mudo
2) un while sin paréntesis en el cuerpo: while (c) x += 1;  (va while (c) ( x += 1; );)
Busca los dos en nube_sampler.jsfx. Sale con 1 si hay alguno."""
import pathlib, re, sys
txt = (pathlib.Path(__file__).resolve().parent.parent / "nube_sampler.jsfx").read_text()
code = re.sub(r"//[^\n]*", "", txt)
code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
defs = {m.group(1).lower(): m.start() for m in re.finditer(r"\bfunction\s+([A-Za-z_][\w.]*)\s*\(", code)}
bad = []
for m in re.finditer(r"\b([A-Za-z_][\w.]*)\s*\(", code):
    name = m.group(1).lower(); pos = m.start()
    if name in defs and defs[name] > pos and not code[max(0, pos - 9):pos].strip().endswith("function"):
        bad.append((code.count("\n", 0, pos) + 1, m.group(1)))
for m in re.finditer(r"\bwhile\s*\(", code):
    d = 0; j = m.end() - 1
    while True:
        d += code[j] == "("; d -= code[j] == ")"
        if d == 0: break
        j += 1
    if not code[j + 1:].lstrip().startswith("("):
        bad.append((code.count("\n", 0, m.start()) + 1, "while sin ( cuerpo )"))
for ln, nm in bad:
    print(f"ORDEN: línea {ln}: {nm}() se usa antes de definirse")
sys.exit(1 if bad else 0)
