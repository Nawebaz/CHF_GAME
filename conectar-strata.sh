#!/usr/bin/env bash
# Conecta Strata (la IA local del PC) con Faro. v2
# - Pregunta al propio Strata (su biblioteca de control, la misma que usa el arranque automático) en qué puerto está su API.
# - Busca la clave en su perfil y en sus procesos, y la prueba SOLO contra localhost (puertos de Strata, nunca otro servicio).
# - Si no la encuentra, te la pide; al escribirla no se ve.
# - Guarda puerto y clave en ~/faro/data/secrets/strata.json (solo tu usuario). Nunca muestra la clave ni la envía fuera del PC.
# Uso desde el Mac:  ssh -t -l iceland -o HostName=iceland iceland 'bash <(curl -fsSL https://raw.githubusercontent.com/Nawebaz/CHF_GAME/faro-buzon/conectar-strata.sh)'
set -u
DIR="$HOME/faro/data/secrets"; DEST="$DIR/strata.json"
code() { curl -s -o /dev/null -w '%{http_code}' -m 5 "${@:2}" "$1/v1/models"; }

echo "1/4 ¿Dónde escucha Strata?"
urls=()
addu() { case " ${urls[*]:-} " in *" $1 "*) ;; *) urls+=("$1");; esac; }
# a) la biblioteca de control de Strata (AppImage montada o código en ~/Strata)
CTRL=$(ls -d /tmp/.mount_Strata*/usr/lib/Strata/control 2>/dev/null | head -1)
PY=""; [ -n "$CTRL" ] && [ -x "$CTRL/python/bin/python3.12" ] && PY="$CTRL/python/bin/python3.12"
if [ -n "$PY" ]; then
  while IFS= read -r u; do [ -n "$u" ] && addu "$u"; done < <(cd "$CTRL" && "$PY" - 2>/dev/null <<'EOF'
from strata_control import runtime
for prof in ("app-1", "app-2", "default"):
    try:
        s = runtime.status(prof) or {}
        u = s.get("api_url") or ""
        if u: print(u.rstrip("/").removesuffix("/v1"))
    except Exception: pass
EOF
)
fi
# b) puertos abiertos por procesos de Strata
while IFS= read -r p; do addu "http://127.0.0.1:$p"; done < <(ss -ltnpH 2>/dev/null | grep -i -E 'strata|llama|python3\.12' | grep -oE '127\.0\.0\.1:[0-9]+|0\.0\.0\.0:[0-9]+|\*:[0-9]+|\[::\]:[0-9]+' | grep -oE '[0-9]+$')
addu "http://127.0.0.1:18500"; addu "http://127.0.0.1:18501"
vivos=()
for u in "${urls[@]}"; do
  case "$u" in *:8080|*:8787|*:8788) continue;; esac   # freqtrade y Faro no son Strata
  c=$(code "$u"); echo "   $u → $c"
  [ "$c" != "000" ] && vivos+=("$u")
  if [ "$c" = "200" ]; then
    mkdir -p "$DIR"; chmod 700 "$DIR"; umask 077
    python3 -c 'import json,sys; json.dump({"url": sys.argv[1]}, open(sys.argv[2], "w"))' "$u" "$DEST"; chmod 600 "$DEST"
    echo "Strata responde sin clave en $u. Guardado el puerto para Faro."; curl -s -m 5 -X POST http://127.0.0.1:8787/api/update >/dev/null 2>&1; exit 0
  fi
done
if [ "${#vivos[@]}" -eq 0 ]; then
  echo "Strata no responde en ningún puerto. Abre la app de Strata y carga el modelo; luego repite esto. No he cambiado nada."
  exit 1
fi

echo "2/4 Busco la clave (no se muestra)"
cands=(); n_proc=0; n_file=0
add() { [ "${#1}" -ge 8 ] && [ "${#1}" -le 400 ] && cands+=("$1"); }
yo=$$
while read -r pid; do
  [ "$pid" = "$yo" ] && continue
  [ -r "/proc/$pid/cmdline" ] || continue
  grep -qa 'conectar-strata' "/proc/$pid/cmdline" 2>/dev/null && continue
  n_proc=$((n_proc+1))
  if [ -r "/proc/$pid/environ" ]; then
    while IFS= read -r -d '' kv; do
      case "${kv%%=*}" in *KEY*|*TOKEN*|*SECRET*|*key*|*token*) add "${kv#*=}";; esac
    done 2>/dev/null < "/proc/$pid/environ"
  fi
  prev=""
  while IFS= read -r -d '' a; do
    case "$prev" in --api-key|--api_key|--apikey|--key|--token|--auth-token|--auth_token) add "$a";; esac
    case "$a" in --api-key=*|--api_key=*|--apikey=*|--key=*|--token=*|--auth-token=*) add "${a#*=}";; esac
    case "$prev" in --api-key-file|--api_key_file|--key-file|--token-file) [ -r "$a" ] && add "$(tr -d '\r\n' < "$a")";; esac
    prev="$a"
  done 2>/dev/null < "/proc/$pid/cmdline"
done < <(ps -eo pid=,args= | grep -i -E 'strata|llama-server' | grep -v grep | awk '{print $1}')
# perfiles y configuración de la app (solo carpetas de Strata)
while IFS= read -r -d '' f; do
  n_file=$((n_file+1))
  while IFS= read -r v; do add "$v"; done < <(grep -hoiE '"?(api[_-]?key|apikey|token|secret|auth[_-]?token|bearer)"?[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9._~+/=#-]{8,}' "$f" 2>/dev/null \
    | sed -E 's/^[^:=]*[:=][[:space:]]*["'"'"']?//; s/["'"'"',]+$//')
  case "$f" in *.key|*/key|*/token|*api_key*|*apikey*) add "$(tr -d '\r\n' < "$f")";; esac
done < <(find "$HOME/.config" "$HOME/.local/share" "$HOME/.local/state" "$HOME/.cache" "$HOME/Strata/data" "$HOME/.strata" -maxdepth 5 -type f -ipath '*strata*' -size -300k \
         \( -iname '*.json' -o -iname '*.toml' -o -iname '*.yaml' -o -iname '*.yml' -o -iname '*.ini' -o -iname '*.conf' -o -iname '*.env' -o -iname '.env' -o -iname '*key*' -o -iname '*token*' -o -iname '*profile*' -o -iname '*settings*' \) -print0 2>/dev/null)
echo "   miré $n_proc procesos de Strata y $n_file archivos de su configuración: ${#cands[@]} posibles claves"

hdr=""; val=""; url=""
probar() {   # $1 = clave; prueba en cada puerto vivo de Strata con las cabeceras habituales
  local u
  for u in "${vivos[@]}"; do
    if [ "$(code "$u" -H "Authorization: Bearer $1")" = "200" ]; then hdr="Authorization"; val="Bearer $1"; url="$u"; return 0; fi
    if [ "$(code "$u" -H "X-API-Key: $1")" = "200" ]; then hdr="X-API-Key"; val="$1"; url="$u"; return 0; fi
    if [ "$(code "$u" -H "api-key: $1")" = "200" ]; then hdr="api-key"; val="$1"; url="$u"; return 0; fi
  done
  return 1
}
echo "3/4 Pruebo las posibles claves contra Strata (solo en este PC)"
for c in "${cands[@]:-}"; do [ -n "$c" ] && probar "$c" && break; done

if [ -z "$hdr" ]; then
  echo "   Ninguna sirve. En la app de Strata, la clave está en el perfil del servidor (API key)."
  printf "   Pégala aquí y pulsa Intro (no se verá al escribir): "
  read -rs k; echo
  k=$(printf '%s' "$k" | tr -d '\r\n' | sed -E 's/^[[:space:]]+|[[:space:]]+$//g')
  if ! probar "$k"; then echo "   Esa clave tampoco abre Strata en ${vivos[*]}. No he guardado nada."; exit 1; fi
fi

echo "4/4 Guardo para Faro"
mkdir -p "$DIR"; chmod 700 "$DIR"; umask 077
python3 -c 'import json,sys; json.dump({"url": sys.argv[1], "header": sys.argv[2], "value": sys.argv[3]}, open(sys.argv[4], "w"))' "$url" "$hdr" "$val" "$DEST"
chmod 600 "$DEST"
mods=$(curl -s -m 5 -H "$hdr: $val" "$url/v1/models" | python3 -c 'import json,sys
try: print(", ".join(m.get("id", "?") for m in json.load(sys.stdin).get("data", []))[:120])
except Exception: print("")' 2>/dev/null)
echo "Listo: Strata en $url acepta la clave (${mods:-modelo sin nombre}). Guardada en $DEST, solo legible por ti; no se ha mostrado."
curl -s -m 5 -X POST http://127.0.0.1:8787/api/update > /dev/null 2>&1 && echo "Faro: pedida la actualización; usará a Strata en cuanto tenga la versión 2.13 (unos minutos)."
