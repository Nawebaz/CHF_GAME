# Radar diario de la máquina de GTA VI

Una tarea programada en la nube deja aquí cada mañana `AAAA-MM-DD.md` (y `AAAA-MM-DD.hechos.jsonl`):

1. **Radar**: los vídeos cortos más virales de ayer en español, inglés y portugués, en el nicho (GTA VI) y en los nichos nodo (Rockstar/Take-Two, lanzamientos y consolas, cultura gamer, bolsa del videojuego, sátira de actualidad).
2. **Dictamen de los jueces** (`../kit/jueces.md`): qué quieren ver mañana y por qué, a partir del radar.
3. **Hechos**: noticias y referencias que respaldan esos temas, cada una con fuente y fecha, en el formato de `../kit/hechos.jsonl`.
4. **Propuestas de guion** según `../kit/guionista.md`, solo con hechos del punto 3.

Hermes: vuelca los hechos nuevos a `~/Descargas/gta6/hechos.jsonl` y crea los clips con `gta.py nuevo`. Nada se publica sin el visto bueno de Nawe y de la dueña de la voz.
