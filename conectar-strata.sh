#!/usr/bin/env bash
# Conecta Strata (la IA local del PC) con Faro.
# - Busca la clave en el propio Strata (su proceso, su carpeta y su configuración) y la prueba SOLO contra localhost.
# - Si no la encuentra, te la pide; al escribirla no se ve.
# - La guarda en ~/faro/data/secrets/strata.json (solo legible por tu usuario). Nunca la muestra ni la envía fuera del PC.
# Uso desde el Mac:  ssh -t -l iceland -o HostName=iceland iceland 'bash <(curl -fsSL https://raw.githubusercontent.com/Nawebaz/CHF_GAME/faro-buzon/conectar-strata.sh)'
set -u
URL="${STRATA_URL:-http://127.0.0.1:18501}"
DIR="$HOME/faro/data/secrets"; DEST="$DIR/strata.json"
code() { curl -s -o /dev/null -w '%{http_code}' -m 5 "$@" "$URL/v1/models"; }

sin=$(code)
if [ "$sin" = "000" ]; then echo "Strata no responde en $URL. ¿Está encendido? No he cambiado nada."; exit 1; fi
if [ "$sin" = "200" ]; then echo "Strata ya responde sin clave: no hace falta nada."; exit 0; fi

# Candidatas, sin enseñarlas nunca
cands=()
add() { [ "${#1}" -ge 8 ] && cands+=("$1"); }
yo=$$
for pid in $(pgrep -f -i 'strata' 2>/dev/null); do
  [ "$pid" = "$yo" ] && continue
  [ -r "/proc/$pid/cmdline" ] || continue
  grep -qa 'conectar-strata' "/proc/$pid/cmdline" 2>/dev/null && continue
  if [ -r "/proc/$pid/environ" ]; then
    while IFS= read -r -d '' kv; do
      case "${kv%%=*}" in *KEY*|*TOKEN*|*SECRET*|*key*|*token*) add "${kv#*=}";; esac
    done < "/proc/$pid/environ"
  fi
  prev=""
  while IFS= read -r -d '' a; do
    case "$prev" in --api-key|--api_key|--apikey|--key|--token|--auth-token|--auth_token) add "$a";; esac
    case "$a" in --api-key=*|--api_key=*|--apikey=*|--key=*|--token=*|--auth-token=*) add "${a#*=}";; esac
    case "$prev" in --api-key-file|--api_key_file|--key-file|--token-file) [ -r "$a" ] && add "$(tr -d '\r\n' < "$a")";; esac
    prev="$a"
  done 2>/dev/null < "/proc/$pid/cmdline"
  cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null); [ -n "$cwd" ] && dirs+=("$cwd")
done
dirs+=("$HOME/.config/strata" "$HOME/.strata" "$HOME/strata" "$HOME/Strata" "$HOME/.config/Strata")
for d in "${dirs[@]:-}"; do
  [ -d "$d" ] || continue
  while IFS= read -r v; do add "$v"; done < <(find "$d" -maxdepth 2 -type f \( -name '.env' -o -name '*.json' -o -name '*.toml' -o -name '*.yaml' -o -name '*.yml' -o -name '*.ini' -o -name '*.conf' -o -name '*key*' -o -name '*token*' \) -size -200k -print0 2>/dev/null \
    | xargs -0 -r grep -hoiE '(api[_-]?key|apikey|token|secret|auth)[^:=]{0,12}[:=][[:space:]]*["'"'"']?[A-Za-z0-9._~+/=-]{8,}' 2>/dev/null \
    | sed -E 's/^[^:=]*[:=][[:space:]]*["'"'"']?//')
  for f in "$d"/*.key "$d"/key "$d"/token; do [ -r "$f" ] && add "$(tr -d '\r\n' < "$f")"; done
done

hdr=""; val=""
probar() {   # $1 = clave; deja en hdr/val la forma que Strata acepta
  if [ "$(code -H "Authorization: Bearer $1")" = "200" ]; then hdr="Authorization"; val="Bearer $1"; return 0; fi
  if [ "$(code -H "X-API-Key: $1")" = "200" ]; then hdr="X-API-Key"; val="$1"; return 0; fi
  return 1
}
for c in "${cands[@]:-}"; do [ -n "$c" ] && probar "$c" && break; done

if [ -z "$hdr" ]; then
  echo "No encuentro la clave de Strata en el PC (he mirado su proceso y su configuración)."
  printf "Pégala aquí y pulsa Intro (no se verá al escribir): "
  read -rs k; echo
  if ! probar "$k"; then echo "Esa clave no abre Strata. No he guardado nada."; exit 1; fi
fi

mkdir -p "$DIR"; chmod 700 "$DIR"
umask 077
python3 -c 'import json,sys; json.dump({"header": sys.argv[1], "value": sys.argv[2]}, open(sys.argv[3], "w"))' "$hdr" "$val" "$DEST"
chmod 600 "$DEST"
mods=$(curl -s -m 5 -H "$hdr: $val" "$URL/v1/models" | python3 -c 'import json,sys
try: print(", ".join(m.get("id", "?") for m in json.load(sys.stdin).get("data", []))[:120])
except Exception: print("")' 2>/dev/null)
echo "Listo: Strata acepta la clave (${mods:-modelo sin nombre}). Guardada en $DEST, solo legible por ti; no se ha mostrado."
curl -s -m 5 -X POST http://127.0.0.1:8787/api/update > /dev/null 2>&1 && echo "Faro: pedida la actualización; usará a Strata en cuanto tenga la versión 2.12 (como mucho unos minutos)."
