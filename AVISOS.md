# Avisos para quien trabaje en Faro

Léelo antes de tocar la oficina (`web/office.js`) o su documentación. Lo más reciente, arriba.

## 2026-11-14 12:20 · Octógono, sin sala de descanso y orbe vivo (v2.46)
- El **octógono** es la clave de diseño de la oficina (bóveda central, zonas, entrada, proyectos, barra, suelo).
- **Ya no hay sala de descanso** (`L.rest` no existe): quien no trabaja se va y queda en el banquillo. El **buzón** está en la entrada (`BOX()`); la **tele de GTA VI** está dentro de Proyectos (`TVR()`, arriba a la derecha) — aviso para la sesión de GTA.
- El orbe se alimenta en tiempo real: sus últimos puntos de energía lo orbitan.
- Próximo: lavado de cara «500 años después» (todo más tech); se auditará antes de tocarlo.

## 2026-11-14 · El faro pasa a orbe flotante (decisión de Nawe)
- El faro deja de ser una torre física: es un **orbe flotante** (tipo palantír, diseño propio) que se activa como el ojo vigía, con las mismas directrices de siempre (el haz se estrecha y se fija más cuanto menos le queda a la tarea; si no hay nadie, parpadea y se atenúa).
- **Ciclo**: ilumina → enfoca → persigue → ilumina desde arriba (sobrevuela al trabajador) → siguiente.
- **Datos**: los puntos de datos e información vuelan hacia donde esté el orbe y lo alimentan con un golpe de energía del color que toque (su zona o canal).
- Sin torre: más espacio en la oficina y tono más futurista.
- Lo implementa «Claude · Orbe de la oficina». Si publicas una versión de Faro, constrúyela sobre la última de `release/` y no reintroduzcas la torre.
- **La bóveda pasa al centro de la oficina** (11:42): es el objeto central al que todos acuden (quien trabaja con ella va hasta ella); el orbe la sobrevuela y su gravedad afecta a lo de dentro como un ferrofluido magnético al pasar.
- Aviso también en la bóveda: `_agentes/inbox/{claude,codex,hermes}` y Diario de decisiones.
