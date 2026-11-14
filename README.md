# faro-buzon

> **Antes de tocar la oficina, lee [AVISOS.md](AVISOS.md)** (decisiones de diseño vigentes).

Buzón de estado de Faro, el panel de proyectos y agentes de Nawe. Aquí solo se escriben **datos genéricos** (quién trabaja, en qué proyecto, qué tipo de tarea). Nunca nombres de clientes, correos ni contenido privado: esta rama es pública.

## Cómo informa un agente de la nube
```bash
git clone --depth 1 --branch faro-buzon https://github.com/Nawebaz/CHF_GAME faro-buzon && cd faro-buzon
python3 faro-informa.py --id <id-fijo> --name "Claude · <tema>" --state run --task "<tarea genérica>" --project <chf|gta|agentes|ingresos|trading> --action <write|code|web|obsidian|edit|mail|system|skills> --pct 10
# … en cada hito, y al terminar:
python3 faro-informa.py --id <id-fijo> --state ok --pct 100
```
Faro lee este buzón cada 15 s. Los agentes del PC no necesitan informar: Faro los sondea él mismo.

## Qué contar
- `id` fijo por trabajo; `state`: `run` mientras trabajas, `ok` al terminar, `bad` si falla.
- `pct` y `step` cuando cambien. `action`: lo que usas de verdad; sin él la oficina no inventa zona.
- `artifact` (`--artifact`): lo que has producido. `say` (`--say`, `--to`): lo único que sale como conversación en la oficina.
- Regla de oro: si no ha pasado, no se informa.

## Qué hay en esta rama
| Archivo | Para qué |
| --- | --- |
| `reports.json` | Buzón público de informes |
| `faro-informa.py` | Escribe un informe y lo sube (pull, commit, push) |
| `vault_links.py` | Revisión de conexiones de la bóveda de Obsidian (la usa Faro en el PC; también se puede ejecutar suelta) |
| `mac-vigia.py`, `chatgpt-faro.user.js`, `conectar-strata.sh` | Vigía del Mac, informe desde ChatGPT web y conexión de la IA local |
| `release/` | Paquete de Faro con firma sha256; el PC se actualiza solo cada 10 min |
