# Avisos para quien trabaje en Faro

Léelo antes de tocar la oficina (`web/office.js`) o su documentación. Lo más reciente, arriba.

## 2026-11-16 16:40 · El bibliotecario sintetizando (v2.79)
- Contrato nuevo: quien sintetice la biblioteca reescribe `~/Biblioteca/sintesis.json` = `{fase, hechas, total, actual, motor}` al menos cada 2 min. Con eso Faro sienta a «Bibliotecario · síntesis» en su mesa; `isBiblio` reconoce los dos nombres (descarga y síntesis). No informes de esa tarea con otro agente duplicado.

## 2026-11-16 14:50 · La bóveda, como el grafo de Obsidian en 3D (v2.78)
- `vault_graph()` devuelve también **etiquetas** (`k: 1`, id `#etiqueta`) y **adjuntos** (`k: 2`, id con extensión). Lo que no tiene enlaces (`d: 0`) va en un cinturón (radio 0,40–0,47); lo enlazado, dentro de 0,31. `o: 3` = adjunto sin enlazar (no es un fallo). La forma ya no depende del calor ni de la carpeta.
- Oficina: **color por conexiones** (`degCol`), no por tránsito; el tránsito es solo un aro que late. Los nodos `ring` no entran en la física. El radio de choque depende del número de notas (`RB`): no vuelvas a poner uno fijo.
- Cámara: `VG.cam.zm` (zoom) y vista completa al abrir. Ojo al editar líneas largas: un `//` a media línea se come el resto (me pasó con `C.until`).

## 2026-11-16 13:55 · Figura propia del bibliotecario (v2.77)
- `isBiblio(a)` reconoce a «Bibliotecario · descarga» **por el nombre**: en `buildAgents` el id es `"a:" + nombre`, no el `live:…` del servidor (ojo si enganchas algo a un agente concreto). `drawLibrarian()` lo dibuja en código y se salta `spAgent`; no le pongas el sprite del faro.
- Pedido por Nawe: le parecía feo el sprite antiguo. Sin créditos de imagen.

## 2026-11-16 13:45 · La descarga de la biblioteca sale como agente (v2.76)
- `biblio_agent()` añade la ficha `live:biblio` («Bibliotecario · descarga») solo mientras `biblio_probe()` dice `running`; su mesa pinta `drawBiblioScreen()`. No lo sustituyas por informes ni lo dejes fijo: si no hay descarga, no hay agente.
- Construido sobre v2.75. Sin validar en pantalla real.

## 2026-11-16 13:05 · Oficina fluida, proyectos fieles y paneles nuevos (v2.75)
- **Rendimiento**: la física de la bóveda (`vgStep`) tiene tope de 3 pasos por fotograma, 14 atractores como mucho y choques por barrido. **No vuelvas a escalar los pasos con el tiempo del fotograma** ni a recorrer «todas las calientes × todas las notas»: con la bóveda entera caliente la oficina cayó a 3 fotogramas/s.
- **Calor**: relativo a la mediana (`vgHeat`); las lecturas con `via: "sistema"` (git, indexadores) no calientan ni en el servidor ni en el cliente.
- **Proyectos**: `build` llega ya resumido (`build_view`: `w7`, `d1`, `total`, 12 últimas). La altura de la aguja es `w7` a escala común. No uses `floors` para dibujar.
- **Paneles**: zonas `voice` («Voz y audio») e `image` («Imagen») en lugar de `mail` y `skills`. Acciones nuevas para informar: `--action voice`, `--action image`. `mail` cae en Escritura y `skills` en Código.

## 2026-11-16 11:10 · Monitor de la biblioteca offline (v2.74)
- Franja al pie de la bóveda: `BBR()`, `bibLive()`, `drawBiblio()` en `office.js`. **Faro sondea él mismo** con `biblio_probe()` (`~/Biblioteca/progreso.json` y `manifest.json`, o `biblioteca.dir`); no lo sustituyas por informes.
- **Contrato para quien descargue** (encargo en la bóveda, `_agentes/inbox/faro`, 16 nov): `progreso.json` = `{nivel, hecho_bytes, total_bytes, actual}`, reescrito al menos cada 2 min mientras se descarga; `manifest.json` = lista de `{id, disciplina[], idioma, licencia, bytes, fecha, sha256, ruta, estado}` con `estado: "ok"` solo tras comprobar el sha256.
- Los archivos de la biblioteca van fuera de la bóveda; en la bóveda solo el catálogo (`30 Recursos/Biblioteca/`).
- Sin validar en pantalla real: si pisa algo del grafo, mueve `BBR()`.

## 2026-11-16 09:05 · Créditos de imagen RESERVADOS para los sprites de Faro (orden de Nawe)
- Hasta nuevo aviso, **ningún agente gasta créditos ni cupo de generación de imágenes** (Astra, Higgsfield, cupo de imágenes de ChatGPT) en nada que no sea el rediseño de Faro y la oficina. Quien los usará es GPT.
- Todo lo demás (CHF, GTA VI, manga, pruebas) se dibuja en código, se hace con el motor local o espera.
- Nadie compra créditos ni cambia de plan. Si una tarea no puede seguir sin gastar, se para y se avisa a Nawe.

## 2026-11-15 22:05 · Expertos en la oficina (v2.71)
- Si trabajas con un papel de experto (los de `20 Áreas/Expertos/` de la bóveda), informa con `--expert "<nombre del experto>"`: la oficina lo muestra con una insignia bajo tus pies mientras estés en `run`. Experto nuevo: «Investigación y fuentes» (dueño del banco de hechos y del radar de GTA VI).
- `gta_probe` rotula cada clip con el `id` de su `clip.json`.

## 2026-11-15 21:50 · Máquinas en directo, ficha de máquina y batería (v2.51–v2.70)
- **Faro sondea él mismo** (no depende de que nadie informe): `voz_probe()` (procesos y audios de `~/FaroTrabajo/voz`) y `gta_probe()` (lee `*/clip.json` bajo `~/Descargas/gta6` o `gta.dir`). Salen en `/api/machines` (`voz`, `gta`) y en el estado (`voz_probe`, `gta_probe`). No los quites ni los sustituyas por informes.
- **Contrato de la máquina de GTA VI**: un `clip.json` por clip, escrito por `gta.py` (kit en la bóveda, `_agentes/adjuntos/gta-maquina/`). Orden de tramos en `GTA_ST`: FUENTES, GUION, ITV GUION, VOZ, CAPTURA, RÓTULOS, MONTAJE, ITV VÍDEO, TALLER, EMPAQUE, PEAJE, PUBLICADO. El montaje va después de la voz. Los números `st` antiguos se conservan: no los renumeres.
- **Ficha de máquina**: clic en el monitor de GTA VI o en el de voz abre `machineSheetHTML(focus)` (hoja ancha `fo-wide`, se refresca sola conservando el scroll).
- **Batería en móvil**: `S.lite` (puntero grueso: 20 fps, 10 en reposo, dpr 1,5) y en `index.html` `LITE/QUIET` (sin lluvia, sondeos lentos, pausa con la pestaña oculta). Cualquier animación nueva debe respetarlos.
- **Orbe**: luz física (`spec()`), haz difuso del color de la tarea con entrada suave (`E.bk`), esquiva los bocadillos (`a.bub`), y deposita por las aristas hasta las notas realmente tocadas (`vgPath`, `VG.log`). Tope de 12 motas.
- **Bóveda**: las llamadas son lanzamientos desde la barandilla que caen bajo el cristal y no salen del octógono (máx. 8 a la vez); los pulsos de conexión son motas, no rayas.
- Agentes: entran y salen por teletransporte (`drawAgent` envuelve a `drawAgentBody`).

## 2026-11-15 09:58 · Monitor permanente de la voz narradora (v2.57)
- Bajo la tele de GTA VI. `vozLive()`/`drawVoz()` en `office.js`; el estado trae `voz_last`. **Quien genere voz debe informar con `--project voz`, `--state run` mientras genera y `ok` al parar**, y si puede el bloque `{"voz": {"paso": "…", "idioma": "es|en|pt", "cola": n, "revisar": n}}` por `--json`.
- Nota para la sesión de tokens: `office.js` de v2.55–v2.56 era el de v2.54 sin cambios; v2.57 lo sustituye. Los colores nuevos de la oficina siguen sin pasar a `tokens.js`.

## 2026-11-14 13:10 · Partículas gravitatorias con sprites de CHF y monitor de GTA VI persistente (v2.48–v2.49)
- Entre la bóveda y el orbe: partículas hechas con sprites del juego CHF (`web/office-chf.webp`: `fx_viento` remolino, `fx_iman` estela, `fx_chispa` llegada), teñidas del color de su nota y luego del orbe (`drawGravity`, `chfTinted`). Si se rehace el atlas, actualiza `CHF.v`.
- El estado trae `gta_last` (último informe con bloque `gta`, aunque sea viejo): la tele de GTA VI no se apaga.
- **Tokens comunes** («Plató nocturno», aviso de las 12:23): cuando lleguen `web/tokens.css`/`tokens.js`, los colores de la oficina (`TX`, `SEGC`, `PNEON`, zonas y canales) deben pasar a los tokens. Constrúyelo sobre la última versión de `release/` (v2.49 o posterior) para no perder lo de hoy.

## 2026-11-14 12:45 · «500 años después», monitor de GTA VI y ruta del orbe (v2.47)
- **Estilo**: cristal oscuro, filos de neón y hologramas, todo dibujado en código (sin créditos). Ayudantes en `office.js`: `txGlass`, `txText`, `txSeg`, `txBeam`, `txBubble`. **No reintroduzcas** el estilo «Bruto» (madera, pergamino, contorno negro): sus funciones ya no existen.
- **Mesas**: `DG(dk)` es geometría de código (tablero `st`, panel `sx/sy/sw/sh`, `top`, `seat`); ya no hay flexo (`lampGeo` eliminado) ni sprite de mesa. Zonas: `ZG()` devuelve `pad` y `scr` (puesto holográfico). Los sprites de mesa, flexo, zonas y buzón siguen en el atlas pero no se usan.
- **Proyectos**: agujas con un segmento por cosa hecha, color por tipo (`SEGC`: cian entregas, violeta artefactos, oro orgullo ×2, gris azulado obra guardada). Alto de segmento: `PFH()` (úsalo también en `buildingTop`).
- **Máquina GTA VI**: `gtaLive()` dice si trabaja (agente de GTA trabajando en la oficina, o informe con `gta` en `run` sin caducar), paso, última señal y recuento. La tele de Proyectos es su monitor, como el de Strata. **Si informas de la máquina, manda `--state run` mientras trabaje y `ok` al parar**, con el bloque `gta` (`--json`), para que la luz sea fiel.
- **Orbe**: mantiene su ruta (orden de mesa, sigue por donde iba si alguien entra o sale); sin trabajo se queda flotando y a los 25 s sobrevuela la bóveda.

## 2026-11-14 12:20 · Octógono, sin sala de descanso y orbe vivo (v2.46)
- El **octógono** es la clave de diseño de la oficina (bóveda central, zonas, entrada, proyectos, barra, suelo).
- **Ya no hay sala de descanso** (`L.rest` no existe): quien no trabaja se va y queda en el banquillo. El **buzón** está en la entrada (`BOX()`); la **tele de GTA VI** está dentro de Proyectos (`TVR()`, arriba a la derecha) — aviso para la sesión de GTA.
- El orbe se alimenta en tiempo real: sus últimos puntos de energía lo orbitan.
- Lavado de cara «500 años después»: hecho en v2.47.

## 2026-11-14 · El faro pasa a orbe flotante (decisión de Nawe)
- El faro deja de ser una torre física: es un **orbe flotante** (tipo palantír, diseño propio) que se activa como el ojo vigía, con las mismas directrices de siempre (el haz se estrecha y se fija más cuanto menos le queda a la tarea; si no hay nadie, parpadea y se atenúa).
- **Ciclo**: ilumina → enfoca → persigue → ilumina desde arriba (sobrevuela al trabajador) → siguiente.
- **Datos**: los puntos de datos e información vuelan hacia donde esté el orbe y lo alimentan con un golpe de energía del color que toque (su zona o canal).
- Sin torre: más espacio en la oficina y tono más futurista.
- Lo implementa «Claude · Orbe de la oficina». Si publicas una versión de Faro, constrúyela sobre la última de `release/` y no reintroduzcas la torre.
- **La bóveda pasa al centro de la oficina** (11:42): es el objeto central al que todos acuden (quien trabaja con ella va hasta ella); el orbe la sobrevuela y su gravedad afecta a lo de dentro como un ferrofluido magnético al pasar.
- Aviso también en la bóveda: `_agentes/inbox/{claude,codex,hermes}` y Diario de decisiones.
