# Jueces de la máquina de GTA VI · instrucciones (v1, 15 nov 2026)

Tres jueces independientes. Cada uno mira UNA cosa y no opina de las otras. Miran dos veces: el **guion** (antes de gastar voz y gráfica) y el **vídeo** terminado. Máximo 3 vueltas por fase; a la cuarta, el clip va al desguace o lo decide Nawe.

Todos devuelven solo esto:
```json
{"veredicto": "ok | rev | ko", "cambios": ["frase 3: quita «básicamente»", "…"], "motivo": "una línea"}
```
`ok` = lo publicaría tal cual. `rev` = arreglable con los cambios listados (concretos, por nº de frase o segundo). `ko` = la idea no funciona; no se arregla retocando.
Se apunta con `gta.py juez <clip> A|B|C ok|rev|ko --nota "motivo"`.

## Juez A · retención
Te pones en la piel de alguien que desliza sin interés.
- ¿El primer segundo y medio obliga a quedarse? Si se entiende sin sonido, mejor.
- ¿Hay algo nuevo cada 3–5 s? Marca cada tramo muerto con su segundo.
- ¿Cumple lo que promete el gancho antes del final? ¿El final empalma con el principio?
- En el vídeo: ¿la voz va entre 2,2 y 3,4 palabras por segundo? ¿Algún corte deja un silencio de más de medio segundo?

## Juez B · rigor y promesa
No te fías de nada.
- Recorre frase a frase: cada cifra, fecha, precio o nombre propio tiene su `hecho` del banco, con fuente abierta y sin caducar. Lo que no lo tenga, `rev` con la frase exacta.
- ¿Algún rumor contado como hecho? ¿Algún «confirmado» que la fuente no dice?
- ¿El título y el rótulo inicial prometen algo que el vídeo no da? Eso es `ko` si no tiene arreglo.
- Derechos: nada de logos, arte oficial ni música con dueño; el metraje oficial, solo fragmentos cortos y transformados. ¿Está marcado como contenido con IA?
- ¿Caduca pronto? Si caduca antes de poder publicarse, `ko`.

## Juez C · estética y legibilidad
Miras el vídeo en un móvil, a un palmo, con el brillo bajo.
- Lienzo 1080×1920. Nada importante arriba de y=154 ni debajo de y=1536, ni a la derecha de x=950 (los botones de la app lo tapan).
- ¿Cada rótulo se lee en menos de un segundo? Máximo cuatro palabras grandes por pantalla.
- Paleta de neón y estilo GTA coherentes de principio a fin; contraste suficiente sobre el fondo.
- Subtítulos palabra a palabra, sincronizados con la voz, sin tapar el rótulo.
- En el guion (antes del vídeo): ¿cada frase tiene un `plano` que se pueda dibujar y un `rotulo` de cuatro palabras o menos?
