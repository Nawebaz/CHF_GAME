# Avisos para quien trabaje en Faro

Léelo antes de tocar la oficina (`web/office.js`) o su documentación. Lo más reciente, arriba.

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
