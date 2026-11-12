#!/usr/bin/env python3
"""Informa a Faro desde cualquier sesión en la nube. Solo datos genéricos: nada de clientes, correos ni contenido privado.
Uso (desde un clon de la rama faro-buzon):
  python3 faro-informa.py --id gta-pipeline --name "Claude · GTA" --state run --task "monta el panel 3D" \
      --project gta --action code --pct 40 --say "Empiezo el panel 3D"
  python3 faro-informa.py --id gta-pipeline --state ok --pct 100 --artifact "Panel GTA" --say "Hecho: panel publicado"
state: run (trabajando) · ok (terminado) · bad (falló). action: code, write, web, edit, think, obsidian, mail, system, skills.
"""
import argparse, datetime, json, os, subprocess, sys, time
p = argparse.ArgumentParser()
for a in ("id", "name", "state", "task", "project", "action", "step", "artifact", "say", "to", "brand"): p.add_argument("--" + a)
p.add_argument("--pct", type=float); p.add_argument("--ttl", type=int, default=3600)
a = p.parse_args()
if not a.id: sys.exit("falta --id")
here = os.path.dirname(os.path.abspath(__file__)); os.chdir(here)
git = lambda *c: subprocess.run(["git", *c], capture_output=True, text=True)
for intento in range(4):
    git("pull", "-q", "--rebase", "origin", "faro-buzon")
    d = json.load(open("reports.json")) if os.path.exists("reports.json") else []
    r = next((x for x in d if x.get("id") == a.id), None)
    if r is None: r = {"id": a.id, "kind": "run", "cloud": True}; d.append(r)
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
    upd = {k: v for k, v in {"name": a.name, "state": a.state, "task": a.task, "project": a.project, "action": a.action,
           "step": a.step, "pct": a.pct, "brand": a.brand or ("claude" if a.name and "claude" in a.name.lower() else None), "ttl": a.ttl}.items() if v is not None}
    r.update(upd); r["src_at"] = now; r["at"] = now; r["cloud"] = True  # Faro solo importa si cambia "at"
    if a.artifact: r["artifact"] = {"name": a.artifact}
    if a.say: r["say"] = {"to": a.to or "Nawe", "text": a.say, "at": now}
    json.dump(d, open("reports.json", "w"), ensure_ascii=False, indent=1)
    git("add", "reports.json"); git("commit", "-qm", "Faro: %s %s" % (a.id, r.get("state", "")))
    if git("push", "-q", "origin", "HEAD:faro-buzon").returncode == 0: print("Faro informado:", a.id, r.get("state")); break
    git("reset", "-q", "--hard", "origin/faro-buzon"); time.sleep(2 + intento * 2)
else: sys.exit("No pude publicar el informe")
