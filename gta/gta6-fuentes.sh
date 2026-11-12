#!/bin/bash
# Máquina GTA VI · fuentes oficiales para el montaje (lo ejecuta Hermes en iceland por orden de Faro).
# Baja vídeos del canal oficial de Rockstar, saca copias de trabajo SIN audio, una voz guía local (Piper)
# y lo empaqueta en partes ≤380 MB que sirve por Tailscale (puerto 8790) y, de respaldo, por el propio Faro.
set -u
DL=$(xdg-user-dir DOWNLOAD 2>/dev/null || echo "$HOME/Descargas")
OUT="$DL/gta6/fuentes"; ENV="$OUT/envio"; PAQ="$OUT/paquete"
mkdir -p "$OUT" "$ENV" "$PAQ"; cd "$OUT" || exit 1
LOG="$OUT/progreso.log"; exec >>"$LOG" 2>&1
echo "== $(date '+%F %T') inicio"
rep(){ curl -s -m 3 -X POST localhost:8787/api/report -H 'Content-Type: application/json' \
  -d "{\"id\":\"hermes-gta-fuentes\",\"kind\":\"agent\",\"name\":\"Hermes · fuentes GTA\",\"project\":\"gta\",\"state\":\"$1\",\"task\":\"Metraje oficial GTA VI\",\"action\":\"web\",\"pct\":$2,\"step\":\"$3\"}" >/dev/null || true; }
rep run 5 "Instalando herramientas"
T="$HOME/gta6-herramientas"
[ -x "$T/bin/python" ] || python3 -m venv "$T"
"$T/bin/pip" install -q -U "yt-dlp[default]" imageio-ffmpeg piper-tts || echo "AVISO pip"
FF=$(command -v ffmpeg || "$T/bin/python" -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
if ! command -v deno >/dev/null && [ ! -x "$HOME/.deno/bin/deno" ]; then curl -fsSL https://deno.land/install.sh | sh -s -- -y >/dev/null 2>&1 || true; fi
export PATH="$HOME/.deno/bin:$PATH"
baja(){ [ -s "$2.mp4" ] && { echo "ya: $2"; return; }
  "$T/bin/yt-dlp" --ffmpeg-location "$FF" -f "bv*[height<=$3]+ba/b[height<=$3]" --merge-output-format mp4 \
    --no-playlist --no-progress -o "$2.%(ext)s" "https://www.youtube.com/watch?v=$1" || echo "FALLO $2"; }
rep run 15 "Bajando tráileres oficiales"
baja rz1B4B2yBZY launch 2160
baja _yl5ELcmugI preload 2160
baja VQRLujxTm3c trailer2 2160
baja QdBZY2fkU-0 trailer1 2160
rep run 35 "Bajando el Extended Look"
baja tJbzMqJGH4k extended 1440
sha256sum *.mp4 > HUELLAS-SHA256.txt
rep run 55 "Copias de trabajo sin audio"
for n in launch preload trailer2 trailer1; do
  [ -s "$n.mp4" ] && "$FF" -v error -y -i "$n.mp4" -an -vf "scale=-2:1440" -c:v libx264 -preset veryfast -crf 21 "$ENV/$n-1440.mp4"
done
[ -s extended.mp4 ] && "$FF" -v error -y -i extended.mp4 -an -vf "scale=-2:1080" -c:v libx264 -preset veryfast -crf 23 \
  -f segment -segment_time 400 -reset_timestamps 1 "$ENV/extended-1080-%d.mp4"
rep run 80 "Voz guía local"
VZ="$ENV/vozguia"; mkdir -p "$VZ"; cd "$VZ"
"$T/bin/python" -m piper.download_voices es_ES-davefx-medium >/dev/null 2>&1 || true
while IFS='|' read -r id txt; do
  [ -n "$id" ] && echo "$txt" | "$T/bin/python" -m piper -m es_ES-davefx-medium -f "$id.wav" >/dev/null 2>&1 || echo "FALLO voz $id"
done <<'LINEAS'
e1_1|En GTA 6 la poli te ficha la ropa.
e1_2|Pero alguien tiene que verte, o saltar una alarma.
e1_3|Coche, ropa, cara... y con quién vas.
e1_4|Cámbiate y les borras pistas.
e1_5|Y vuelven las seis estrellas.
e1_6|¿Esto hace GTA mejor... o un rollo?
e2_1|GTA 6: hasta doscientos doce gigas. ¿Te cabe?
e2_2|Una PS5 original te deja seiscientos sesenta y siete útiles.
e2_3|Casi un tercio, para Leonida.
e2_4|Y la caja no trae disco: trae un código.
e2_5|La precarga digital ya está abierta. Borra hoy.
e2_6|¿Qué juego vas a borrar?
p1_1|Esta montaña no existe en Florida.
p1_2|Lo más alto allí: ciento cinco metros.
p1_3|Rockstar se la ha inventado: Mount Kalaga.
p1_4|¿Cagada o acierto?
LINEAS
cd "$OUT"
rep run 90 "Empaquetando"
rm -f "$PAQ"/gta6-paquete.part-*
tar -cf - -C "$ENV" . | split -b 380m -d - "$PAQ/gta6-paquete.part-"
( cd "$PAQ" && sha256sum gta6-paquete.part-* > HUELLAS.txt && ls -l > LISTO.txt )
# servir por Tailscale 10 h; de respaldo, copia en la carpeta web de Faro (solo sirve .png, de ahí el nombre)
pkill -f "http.server 8790" 2>/dev/null; nohup timeout 10h python3 -m http.server 8790 --directory "$PAQ" >/dev/null 2>&1 &
FP=$(pgrep -f "faro.py" | head -1); FW=""
[ -n "$FP" ] && FW="$(dirname "$(readlink -f "$(tr '\0' '\n' < /proc/$FP/cmdline | grep -m1 'faro.py')" 2>/dev/null)")/web"
if [ -d "$FW" ]; then for p in "$PAQ"/gta6-paquete.part-*; do cp "$p" "$FW/gta6-$(basename "$p" | sed 's/gta6-paquete.part-/p/').png"; done
  cp "$PAQ/HUELLAS.txt" "$FW/gta6-huellas.png"; fi
echo "== $(date '+%F %T') LISTO · partes: $(ls "$PAQ"/gta6-paquete.part-* | wc -l) · web Faro: ${FW:-no}"
rep ok 100 "Paquete listo en :8790"
