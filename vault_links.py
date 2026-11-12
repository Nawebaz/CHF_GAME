"""Revisión de conexiones de la bóveda de Obsidian (Faro).

Detecta huérfanas, enlaces rotos, duplicados y encargos viejos; arregla solo lo seguro:
- une encargo ↔ respuesta (notas de _agentes),
- mantiene bloques automáticos en las notas índice (entre marcadores, sin tocar lo escrito a mano),
- aparta las copias de conflicto de Syncthing a _to_delete/.
Nunca borra, nunca toca una nota editada hace menos de 90 s y nunca reescribe texto fuera de sus bloques.
Uso suelto:  python3 vault_links.py RUTA_BOVEDA [--apply]
"""
import hashlib, os, re, shutil, sys, time, unicodedata

NFC = lambda s: unicodedata.normalize("NFC", s)
KEY = lambda s: NFC(s).strip().lower()
LINK = re.compile(r"!?\[\[([^\]|#^]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)
RESP = " · RESPUESTA"
FRESH = 90
SKIP_DIRS = {".obsidian", ".trash", ".git", "_to_delete"}
# Notas que pueden quedar solas a propósito
LONE_OK = re.compile(r"(^|/)(prueba-[^/]*|Bienvenido|LEEME)\.md$|^99 Plantillas/|^01 Bandeja/|^_adjuntos/")
AUTO_A, AUTO_B = "<!-- faro:auto:%s -->", "<!-- /faro:auto:%s -->"

def scan(root):
    notes = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            if not fn.endswith(".md"): continue
            fp = os.path.join(dp, fn); rel = NFC(os.path.relpath(fp, root)).replace(os.sep, "/")
            try:
                with open(fp, encoding="utf-8", errors="replace") as f: txt = f.read()
                notes[rel] = {"fp": fp, "txt": txt, "mtime": os.path.getmtime(fp)}
            except OSError: pass
    return notes

def aliases(txt):
    m = re.match(r"---\n(.*?)\n---", txt, re.S)
    if not m: return []
    a = re.search(r"^aliases:\s*\[(.*?)\]", m.group(1), re.M)
    return [x.strip(" '\"") for x in a.group(1).split(",")] if a else []

def graph(notes):
    idx, base_count = {}, {}
    for rel, n in notes.items():
        b = KEY(os.path.basename(rel)[:-3]); base_count[b] = base_count.get(b, 0) + 1
        idx.setdefault(b, rel); idx[KEY(rel[:-3])] = rel
        for a in aliases(n["txt"]): idx.setdefault(KEY(a), rel)
    out = {r: set() for r in notes}; inc = {r: set() for r in notes}; broken = []
    for rel, n in notes.items():
        for t in LINK.findall(CODE.sub("", n["txt"])):
            t = t.strip()
            if not t or re.search(r"\.(png|jpe?g|webp|gif|pdf|mp4|mov|svg)$", t, re.I): continue
            q = idx.get(KEY(t)) or idx.get(KEY(t.split("/")[-1]))
            if q is None:
                if not rel.startswith("01 Bandeja/"): broken.append((rel, t))
            elif q != rel: out[rel].add(q); inc[q].add(rel)
    ambiguous = sorted(b for b, c in base_count.items() if c > 1)
    return out, inc, broken, ambiguous

def wikilink(rel, alias=None):
    t = rel[:-3]
    return "[[%s|%s]]" % (t, alias) if alias else "[[%s]]" % t

def title(rel):
    return os.path.basename(rel)[:-3]

def set_block(txt, name, lines, heading):
    a, b = AUTO_A % name, AUTO_B % name
    block = "%s\n%s\n%s" % (a, "\n".join(lines) if lines else "- (nada)", b)
    if a in txt and b in txt:
        return re.sub(re.escape(a) + r".*?" + re.escape(b), lambda m: block, txt, flags=re.S)
    return txt.rstrip() + "\n\n## %s\n%s\n" % (heading, block)

class Writer:
    def __init__(self, notes, apply):
        self.notes, self.apply, self.changed, self.skipped = notes, apply, [], []
    def write(self, rel, new):
        n = self.notes[rel]
        if new == n["txt"]: return False
        if time.time() - n["mtime"] < FRESH: self.skipped.append(rel); return False
        if self.apply:
            with open(n["fp"], "w", encoding="utf-8") as f: f.write(new)
            n["txt"], n["mtime"] = new, time.time()
        self.changed.append(rel); return True

def related(txt, links):
    new = [l for l in links if l.split("|")[0].rstrip("]") not in txt]
    if not new: return txt
    if "\n## Relacionado\n" in txt: return txt.rstrip() + "\n" + "\n".join("- " + l for l in new) + "\n"
    return txt.rstrip() + "\n\n## Relacionado\n" + "\n".join("- " + l for l in new) + "\n"

def review(root, apply=False, extra_blocks=None):
    notes = scan(root); W = Writer(notes, apply); moved = []
    # 1) copias de conflicto de Syncthing → _to_delete (nunca se borran)
    for rel in [r for r in notes if ".sync-conflict-" in r]:
        if apply:
            dst = os.path.join(root, "_to_delete"); os.makedirs(dst, exist_ok=True)
            shutil.move(notes[rel]["fp"], os.path.join(dst, os.path.basename(notes[rel]["fp"])))
        moved.append(rel); notes.pop(rel)
    # 2) encargo ↔ respuesta
    by_title = {}
    for rel in notes: by_title.setdefault(KEY(title(rel)), []).append(rel)
    for rel in list(notes):
        if not rel.startswith("_agentes/") or RESP not in title(rel): continue
        for enc in by_title.get(KEY(title(rel).replace(RESP, "")), []):
            if not enc.startswith("_agentes/"): continue
            W.write(rel, related(notes[rel]["txt"], [wikilink(enc, "encargo")]))
            W.write(enc, related(notes[enc]["txt"], [wikilink(rel, "respuesta")]))
    # 3) bloques automáticos en las notas índice
    hub = lambda *c: next((r for r in c if r in notes), None)
    faro, idx_t, inicio = hub("10 Proyectos/Faro.md"), hub("_agentes/Índice de tareas.md"), hub("00 Inicio.md")
    if faro:
        fl = sorted([r for r in notes if r.startswith("Faro/") and not title(r).startswith("Estado ")], key=lambda r: -notes[r]["mtime"])[:40]
        est = sorted([r for r in notes if r.startswith("Faro/Estado ")], reverse=True)[:7]
        lines = ["- " + wikilink(r, title(r)) for r in fl]
        if est: lines.append("- Partes diarios: " + " · ".join(wikilink(r, title(r).replace("Estado ", "")) for r in est))
        W.write(faro, set_block(notes[faro]["txt"], "faro", lines, "Órdenes, auditorías y partes (automático)"))
    if idx_t:
        txt = notes[idx_t]["txt"]; head = txt.split(AUTO_A % "agentes")[0]
        ag = sorted([r for r in notes if r.startswith("_agentes/") and r != idx_t and r != "_agentes/README.md"
                     and RESP not in title(r) and r[:-3] not in head], key=lambda r: -notes[r]["mtime"])[:40]
        lines = []
        for r in ag:
            resp = [x for x in by_title.get(KEY(title(r) + RESP), []) if x in notes]
            st = "respondido" if resp else ("pendiente" if "/inbox/" in r else "archivo")
            lines.append("- " + wikilink(r, title(r)) + (" · " + wikilink(resp[0], "respuesta") if resp else "") + " · " + st)
        W.write(idx_t, set_block(txt, "agentes", lines, "Movimientos del buzón (automático)"))
    for name, rel, lines, heading in (extra_blocks or []):
        if rel in notes: W.write(rel, set_block(notes[rel]["txt"], name, lines, heading))
    # 4) huérfanas de primer nivel (proyectos, áreas, recursos) → bloque en Inicio
    out, inc, broken, ambiguous = graph(notes)
    if inicio:
        top = [r for r in notes if re.match(r"(10 Proyectos|20 Áreas|30 Recursos)/[^/]+\.md$", r) and not (inc[r] - {inicio})]
        top = [r for r in top if r[:-3] not in notes[inicio]["txt"].split(AUTO_A % "inicio")[0] and title(r) not in notes[inicio]["txt"].split(AUTO_A % "inicio")[0]]
        W.write(inicio, set_block(notes[inicio]["txt"], "inicio", ["- " + wikilink(r, title(r)) for r in sorted(top)], "Sin colocar todavía (automático)"))
        out, inc, broken, ambiguous = graph(notes)
    # 5) diagnóstico final
    orphans = sorted(r for r in notes if not inc[r] and r != inicio and not LONE_OK.search(r) and not r.endswith("/Conexiones de la bóveda.md"))
    dup = {}
    for r, n in notes.items():
        body = re.sub(r"\s+", " ", re.sub(r"<!-- faro:auto.*?/faro:auto:\w+ -->", "", n["txt"], flags=re.S)).strip()
        if len(body) > 40: dup.setdefault(hashlib.sha1(body.encode()).hexdigest(), []).append(r)
    dups = [v for v in dup.values() if len(v) > 1]
    stale = []
    for r in notes:
        if "/inbox/" in r and any(x for x in by_title.get(KEY(title(r) + RESP), []) if "done" in notes.get(x, {}).get("txt", "")[:300]):
            if time.time() - notes[r]["mtime"] > 86400: stale.append(r)
    return {"notes": len(notes), "orphans": orphans, "broken": sorted(set(broken)), "ambiguous": ambiguous,
            "duplicates": dups, "stale": sorted(stale), "conflicts_moved": moved,
            "changed": sorted(set(W.changed)), "skipped": sorted(set(W.skipped))}

def report_md(r, when):
    L = ["# Conexiones de la bóveda", "", "Revisión automática de Faro: %s. %d notas." % (when, r["notes"]), "",
         "Se arregla solo: encargo ↔ respuesta, bloques automáticos de los índices y copias de conflicto. Lo de abajo necesita criterio.", ""]
    def sec(h, items, fmt):
        L.append("## %s (%d)" % (h, len(items))); L.extend(fmt(x) for x in items) if items else L.append("- Nada."); L.append("")
    sec("Enlaces rotos", r["broken"], lambda x: "- %s → `%s`" % (wikilink(x[0], title(x[0])), x[1]))
    sec("Huérfanas", r["orphans"], lambda x: "- " + wikilink(x, title(x)))
    sec("Posibles duplicados (mismo texto)", r["duplicates"], lambda v: "- " + " = ".join(wikilink(x, title(x)) for x in v))
    sec("Mismo nombre en varias carpetas (enlace ambiguo)", r["ambiguous"], lambda x: "- " + x)
    sec("Encargos ya respondidos que siguen en inbox (>24 h)", r["stale"], lambda x: "- " + wikilink(x, title(x)))
    sec("Copias de conflicto apartadas a _to_delete", r["conflicts_moved"], lambda x: "- " + x)
    L += ["", "[[10 Proyectos/Faro|Faro]] · [[_agentes/Índice de tareas|Tareas de agentes]]"]
    return "\n".join(L) + "\n"

if __name__ == "__main__":
    root = sys.argv[1]; apply = "--apply" in sys.argv
    r = review(root, apply)
    for k in ("changed", "skipped", "conflicts_moved", "broken", "orphans", "duplicates", "ambiguous", "stale"):
        print("%s (%d):" % (k, len(r[k])), *(["  %s" % (x,) for x in r[k]] or ["  -"]), sep="\n")
    if apply:
        p = os.path.join(root, "Faro", "Conexiones de la bóveda.md"); os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f: f.write(report_md(r, time.strftime("%d/%m/%Y %H:%M")))
