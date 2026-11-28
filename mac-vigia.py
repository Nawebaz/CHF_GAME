#!/usr/bin/env python3
"""Vigía de Faro para el Mac: mira si Codex (app o terminal) está trabajando y se lo cuenta a Faro en el PC.
Instalar (una vez):  python3 mac-vigia.py --instalar          Quitar:  python3 mac-vigia.py --quitar
Lee ~/.codex/sessions (si Codex trabaja y en qué) y el uso de CPU, RAM y gráfica del Mac (cada 3 s). Se actualiza solo una vez por hora."""
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

def _run(cmd, t=4):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=t).stdout
    except Exception: return ""

def _top_ahora(ncpu):
    """CPU real de este segundo con «top» (la 1.ª muestra de top es la media desde el arranque: se usa la 2.ª)."""
    out = _run(["top", "-l", "2", "-s", "1", "-n", "8", "-o", "cpu", "-stats", "command,cpu"], 6)
    parts = out.split("Processes:")
    if len(parts) < 3: return None, []
    last = parts[-1]; m = re.search(r"CPU usage:.*?([\d.]+)% idle", last)
    if not m: return None, []
    procs, on = [], False
    for ln in last.splitlines():
        if ln.strip().startswith("COMMAND"): on = True; continue
        if on and ln.strip():
            p = ln.rsplit(None, 1)
            try: procs.append((float(p[1]), 0, p[0].strip()))
            except (ValueError, IndexError): pass
    return round(max(0.0, 100 - float(m.group(1))), 1), procs

def maquina():
    """CPU, RAM y gráfica del Mac sin sudo: ps, vm_stat/sysctl e ioreg (Apple Silicon da el uso de la GPU ahí)."""
    ncpu = os.cpu_count() or 1
    cpu, procs = _top_ahora(ncpu)
    if cpu is None:   # respaldo: «ps» da medias de un minuto, se mueve despacio
        for ln in _run(["ps", "-Ao", "pcpu=,rss=,comm="]).splitlines():
            p = ln.split(None, 2)
            if len(p) == 3:
                try: procs.append((float(p[0]), int(p[1]), os.path.basename(p[2])))
                except ValueError: pass
        cpu = min(100.0, sum(x[0] for x in procs) / ncpu)
    total = int((_run(["sysctl", "-n", "hw.memsize"]).strip() or "0"))
    vm = _run(["vm_stat"]); pg = int((re.search(r"page size of (\d+)", vm) or [0, 16384])[1])
    get = lambda k: int((re.search(k + r":\s+(\d+)", vm) or [0, 0])[1])
    used = (get("Pages active") + get("Pages wired down") + get("Pages occupied by compressor")) * pg
    io = _run(["ioreg", "-r", "-d", "1", "-w", "0", "-c", "IOAccelerator"])
    g = re.search(r'"Device Utilization %"\s*=\s*(\d+)', io); gm = re.search(r'"In use system memory"\s*=\s*(\d+)', io)
    top = sorted(procs, reverse=True)[:5]
    t_cpu = temperatura()
    return {"name": "Mac", "gpu_temp": _TEMP.get("gpu"), "kind": "mac", "cpu": round(cpu, 1), "ncpu": ncpu,
            "ram": round(used / total * 100, 1) if total else None, "ram_gb": round(used / 2**30, 1), "ram_total_gb": round(total / 2**30, 1),
            "gpu": int(g.group(1)) if g else None, "vram_gb": round(int(gm.group(1)) / 2**30, 1) if gm else None, "cpu_temp": t_cpu, "vigia": VIGIA_V, "temp_diag": _TEMP.get("diag"),
            "top": [{"name": n[:28], "cpu": round(c / ncpu, 1)} for c, _, n in top if c > 1]}

VIGIA_V = "2026.11.28b"
TEMP_PY = r"""
import ctypes, ctypes.util, sys
def lib(n):
    for p in (ctypes.util.find_library(n), "/System/Library/Frameworks/%s.framework/%s" % (n, n)):
        try:
            if p: return ctypes.cdll.LoadLibrary(p)
        except OSError: pass
    raise OSError("no carga " + n)
IO = lib('IOKit'); CF = lib('CoreFoundation')
vp = ctypes.c_void_p
CF.CFStringCreateWithCString.restype = vp; CF.CFStringCreateWithCString.argtypes = [vp, ctypes.c_char_p, ctypes.c_uint32]
CF.CFNumberCreate.restype = vp; CF.CFNumberCreate.argtypes = [vp, ctypes.c_long, vp]
CF.CFDictionaryCreate.restype = vp; CF.CFDictionaryCreate.argtypes = [vp, ctypes.POINTER(vp), ctypes.POINTER(vp), ctypes.c_long, vp, vp]
CF.CFArrayGetCount.restype = ctypes.c_long; CF.CFArrayGetCount.argtypes = [vp]
CF.CFArrayGetValueAtIndex.restype = vp; CF.CFArrayGetValueAtIndex.argtypes = [vp, ctypes.c_long]
IO.IOHIDEventSystemClientCreate.restype = vp; IO.IOHIDEventSystemClientCreate.argtypes = [vp]
IO.IOHIDEventSystemClientSetMatching.argtypes = [vp, vp]
IO.IOHIDEventSystemClientCopyServices.restype = vp; IO.IOHIDEventSystemClientCopyServices.argtypes = [vp]
IO.IOHIDServiceClientCopyEvent.restype = vp; IO.IOHIDServiceClientCopyEvent.argtypes = [vp, ctypes.c_int64, ctypes.c_int32, ctypes.c_int64]
IO.IOHIDEventGetFloatValue.restype = ctypes.c_double; IO.IOHIDEventGetFloatValue.argtypes = [vp, ctypes.c_int32]
IO.IOHIDServiceClientCopyProperty.restype = vp; IO.IOHIDServiceClientCopyProperty.argtypes = [vp, vp]
CF.CFStringGetCString.restype = ctypes.c_bool; CF.CFStringGetCString.argtypes = [vp, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]
CF.CFGetTypeID.restype = ctypes.c_ulong; CF.CFGetTypeID.argtypes = [vp]; CF.CFStringGetTypeID.restype = ctypes.c_ulong
s = lambda t: CF.CFStringCreateWithCString(None, t, 0x08000100)
def num(v): x = ctypes.c_int32(v); return CF.CFNumberCreate(None, 3, ctypes.byref(x))
keys = (vp * 2)(s(b'PrimaryUsagePage'), s(b'PrimaryUsage')); vals = (vp * 2)(num(0xff00), num(5))
cb = lambda n: ctypes.addressof(ctypes.c_char.in_dll(CF, n))
d = CF.CFDictionaryCreate(None, keys, vals, 2, cb('kCFTypeDictionaryKeyCallBacks'), cb('kCFTypeDictionaryValueCallBacks'))
def nombre(svc):
    try:
        p = IO.IOHIDServiceClientCopyProperty(svc, s(b'Product')); buf = ctypes.create_string_buffer(128)
        return buf.value.decode('utf-8', 'replace') if p and CF.CFGetTypeID(p) == CF.CFStringGetTypeID() and CF.CFStringGetCString(p, buf, 128, 0x08000100) else ''
    except Exception: return ''
c = IO.IOHIDEventSystemClientCreate(None); IO.IOHIDEventSystemClientSetMatching(c, d); sv = IO.IOHIDEventSystemClientCopyServices(c); pares = []; ne = 0
n = CF.CFArrayGetCount(sv) if sv else 0
for i in range(n):
    svc = CF.CFArrayGetValueAtIndex(sv, i); e = IO.IOHIDServiceClientCopyEvent(svc, 15, 0, 0)
    if e:
        ne += 1; pares.append([nombre(svc), round(IO.IOHIDEventGetFloatValue(e, 15 << 16), 1)])
sys.stderr.write('cliente=%s servicios=%d eventos=%d con_nombre=%d' % (bool(c), n, ne, sum(1 for x in pares if x[0])))
import json; print(json.dumps(pares))
"""
_TEMP = {"fallos": 0, "v": None, "gpu": None, "t": 0.0, "diag": None}
SENS_CPU = ("pACC MTR", "eACC MTR", "PMU tdie", "SOC MTR")
SENS_GPU = ("GPU MTR",)
SENS_NO = ("tcal", "battery", "gas gauge", "nand")   # «PMU tcal» es de calibración: ~51,8 °C fijo, no mide el chip

def elegir(pares):
    """(nombre, °C) de cada sensor HID → (CPU, GPU). CPU: lo más caliente de núcleos y troquel; GPU: lo más caliente de la gráfica.
    Fuera calibración, batería y NAND. Si macOS no da nombres, lo más caliente de todo (como antes)."""
    ok = [(str(n or ""), float(v)) for n, v in pares if v is not None and 10 < float(v) < 125]
    if not any(n for n, _ in ok):
        return (round(max(v for _, v in ok)) if ok else None, None, "sin nombres")
    ok = [(n, v) for n, v in ok if not any(b in n.lower() for b in SENS_NO)]
    cpu = [(v, n) for n, v in ok if n.startswith(SENS_CPU)] or [(v, n) for n, v in ok if not (n.startswith(SENS_GPU) or "gpu" in n.lower())]
    gpu = [(v, n) for n, v in ok if n.startswith(SENS_GPU) or "gpu" in n.lower()]
    c, g = (max(cpu) if cpu else None), (max(gpu) if gpu else None)
    return (round(c[0]) if c else None, round(g[0]) if g else None, "cpu=%s gpu=%s" % (c[1] if c else "-", g[1] if g else "-"))
def resumen(pares, ancho=170):
    """Familias de sensores (nombre sin el número final) con cuántos hay y su máximo, en páginas que caben en temp_diag."""
    fam = {}
    for n, v in pares:
        k = re.sub(r"\s*\d+$", "", str(n or "?"))[:24]; c, m = fam.get(k, (0, 0.0)); fam[k] = (c + 1, max(m, float(v or 0)))
    items = ["%s×%d %.0f" % (k, c, m) for k, (c, m) in sorted(fam.items())]
    pags, cur = [], ""
    for it in items:
        if cur and len(cur) + len(it) + 2 > ancho: pags.append(cur); cur = it
        else: cur = (cur + "; " + it) if cur else it
    if cur: pags.append(cur)
    return pags

def temperatura():
    """Lo más caliente del chip (Apple Silicon), sin sudo: sensores HID del sistema. Va en un proceso aparte para que,
    si en algún macOS falla, no se lleve por delante al vigía; tras tres fallos seguidos deja de intentarlo."""
    if _TEMP["fallos"] >= 3: return None
    if time.time() - _TEMP["t"] < 9: return _TEMP["v"]
    _TEMP["t"] = time.time()
    try:
        r = subprocess.run([sys.executable, "-c", TEMP_PY], capture_output=True, text=True, timeout=5); out = r.stdout.strip()
        _TEMP["diag"] = ("py%d.%d rc=%s " % (sys.version_info[0], sys.version_info[1], r.returncode) + (r.stderr.strip().splitlines() or [""])[-1])[:200]
        cpu, gpu, quien = elegir(json.loads(out))
        _TEMP["v"], _TEMP["gpu"] = cpu, gpu; _TEMP["fallos"] = 0 if cpu else _TEMP["fallos"] + 1
        _TEMP["diag"] = (_TEMP["diag"] + " " + quien)[:200]
        _TEMP["n"] = _TEMP.get("n", 0) + 1
        pags = resumen(json.loads(out))
        if pags and _TEMP["n"] % 2 == 0:   # una lectura de cada dos: una página del listado de sensores (temporal, para afinar la gráfica)
            k = (_TEMP["n"] // 2) % len(pags); _TEMP["diag"] = ("sens %d/%d: %s" % (k + 1, len(pags), pags[k]))[:200]
    except Exception as e: _TEMP["fallos"] += 1; _TEMP["v"] = _TEMP["gpu"] = None; _TEMP["diag"] = ((_TEMP.get("diag") or "") + " | " + repr(e))[:200]
    return _TEMP["v"]

def enviar_maquina(m):
    for u in FAROS:
        try:
            req = urllib.request.Request(u + "/api/machine", data=json.dumps(m).encode(), headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=4).read(); return
        except Exception: pass

URL_YO = "https://raw.githubusercontent.com/Nawebaz/CHF_GAME/faro-buzon/mac-vigia.py"
def autoactualizar():
    """Una vez por hora: si hay una versión nueva del vigía en el buzón de Faro, se reemplaza y se reinicia (launchd lo vuelve a lanzar)."""
    try:
        nuevo = urllib.request.urlopen(URL_YO + "?t=%d" % time.time(), timeout=15).read()
        yo = os.path.abspath(__file__)
        if nuevo and nuevo != open(yo, "rb").read():
            compile(nuevo, "vigia.py", "exec")
            with open(yo + ".tmp", "wb") as f: f.write(nuevo)
            os.replace(yo + ".tmp", yo); print("vigía actualizado; reinicio", flush=True); sys.exit(0)
    except SystemExit: raise
    except Exception as e: print("autoactualización:", e, flush=True)

def bucle():
    ultimo, t_codex, t_upd = None, 0, time.time()
    while True:
        try: enviar_maquina(maquina())          # cada 3 s: lo más en vivo posible sin cargar el Mac
        except Exception as e: print("máquina:", e, flush=True)
        if time.time() - t_codex > 20:
            t_codex = time.time()
            try:
                r = estado()
                if r and (r != ultimo or int(time.time()) % 60 < 20): enviar(r); ultimo = r
            except Exception as e:
                print("vigía:", e, flush=True)
        if time.time() - t_upd > 3600: t_upd = time.time(); autoactualizar()
        time.sleep(3)

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
    print("Vigía instalado. Avisará a Faro (%s) de lo que haga Codex en este Mac y de su CPU y gráfica." % FARO)

if __name__ == "__main__":
    if "--instalar" in sys.argv: instalar()
    elif "--quitar" in sys.argv:
        subprocess.run(["launchctl", "unload", PLIST]); os.path.exists(PLIST) and os.remove(PLIST); print("Vigía quitado.")
    else: bucle()
