#!/usr/bin/env python3
"""Vigía de Faro para el Mac: mira si Codex (app o terminal) está trabajando y se lo cuenta a Faro en el PC.
Instalar (una vez):  python3 mac-vigia.py --instalar          Quitar:  python3 mac-vigia.py --quitar
Solo lee ~/.codex/sessions. Manda a Faro: si está activo, qué tipo de acción hace y la primera frase del encargo."""
import json, os, re, shutil, subprocess, sys, time, urllib.request
FARO = os.environ.get("FARO_URL", "http://iceland:8787")
FAROS = [FARO] + [u for u in ("http://iceland:8787", "http://192.168.18.108:8787") if u != FARO]
HOME = os.path.expanduser("~")
DEST = os.path.join(HOME, "Library", "Application Support", "FaroVigia")
PLIST = os.path.join(HOME, "Library", "LaunchAgents", "com.faro.vigia.plist")
ACT = [("apply_patch", "code", "edita código"), ("web_search", "web", "busca en la web"), ("update_plan", "think", "planifica"),
       ("shell", "system", "ejecuta comandos"), ("exec_command", "system", "ejecuta comandos")]

def estado(root=os.path.join(HOME, ".codex", "sessions")):
    newest = None
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".jsonl"):
                fp = os.path.join(dp, fn); m = os.path.getmtime(fp)
                if not newest or m > newest[0]: newest = (m, fp)
    if not newest: return None
    busy = time.time() - newest[0] < 120
    with open(newest[1], "rb") as f:
        head = f.read(40000).decode("utf-8", "replace").splitlines()
        f.seek(0, 2); n = f.tell(); f.seek(max(0, n - 60000)); tail = f.read().decode("utf-8", "replace").splitlines()
    task = ""
    for ln in head:
        if '"role": "user"' in ln or '"role":"user"' in ln or "user_message" in ln:
            m = re.search(r'"(?:text|message)"\s*:\s*"((?:[^"\\]|\\.){8,})"', ln)
            if m and not m.group(1).startswith("<"):
                task = json.loads('"%s"' % m.group(1))[:70]; break
    action, label = None, ""
    for ln in reversed(tail[-80:]):
        hit = next(((a, l) for k, a, l in ACT if '"%s"' % k in ln), None)
        if hit: action, label = hit; break
    return {"id": "codex-mac", "kind": "agent", "name": "Codex · Mac", "brand": "gpt", "state": "run" if busy else "ok",
            "action": action if busy else None, "ttl": 300,
            "task": ((label + " · ") if busy and label else "") + (task or ("activo" if busy else "sin actividad reciente"))}

def enviar(r):
    err = None
    for u in FAROS:  # Tailscale primero; la IP de casa como reserva
        try:
            req = urllib.request.Request(u + "/api/report", data=json.dumps(r).encode(), headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=5).read(); return
        except Exception as e: err = e
    raise err

def bucle():
    ultimo = None
    while True:
        try:
            r = estado()
            if r and (r != ultimo or int(time.time()) % 60 < 20): enviar(r); ultimo = r
        except Exception as e:
            print("vigía:", e, flush=True)
        time.sleep(20)

def instalar():
    os.makedirs(DEST, exist_ok=True); shutil.copy(__file__, os.path.join(DEST, "vigia.py"))
    os.makedirs(os.path.dirname(PLIST), exist_ok=True)
    with open(PLIST, "w") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.faro.vigia</string>
<key>ProgramArguments</key><array><string>{sys.executable}</string><string>{os.path.join(DEST, "vigia.py")}</string></array>
<key>EnvironmentVariables</key><dict><key>FARO_URL</key><string>{FARO}</string></dict>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
<key>StandardErrorPath</key><string>{os.path.join(DEST, "vigia.log")}</string>
</dict></plist>""")
    subprocess.run(["launchctl", "unload", PLIST], capture_output=True)
    subprocess.run(["launchctl", "load", PLIST], check=True)
    print("Vigía instalado. Avisará a Faro (%s) de lo que haga Codex en este Mac." % FARO)

if __name__ == "__main__":
    if "--instalar" in sys.argv: instalar()
    elif "--quitar" in sys.argv:
        subprocess.run(["launchctl", "unload", PLIST]); os.path.exists(PLIST) and os.remove(PLIST); print("Vigía quitado.")
    else: bucle()
