"""Standalone CHF music-list joke: original code-generated chiptune, no gameplay."""
import json
import math
import struct
import subprocess
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
W, H, FPS, N = 540, 960, 30, 300
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
GOLD, INK, WHITE = '#ffd46d', '#101925', '#f5ead1'
ENTRIES = [
    ('7', 'Eso no es lo que dije', '0:00', 1.50),
    ('6', 'Cortina de humo', '∞', 2.26),
    ('5', 'Decretito', '3:15', 3.09),
    ('4', 'Rueda de prensa', '0:33', 3.76),
    ('3', 'Cambio de opinión', '4 años', 4.64),
    ('2', 'Me aforo', '0:80', 5.47),
]
DETAIL = {'6': '(en directo)', '4': '(sin preguntas)', '3': '(versión extendida)', '2': '(intro)'}
REVEAL, REORDER, RETURN = 7.34, 8.43, 9.34
FT = lambda size, bold=True: ImageFont.truetype(FONT if bold else REGULAR, size)


def art_and_sprite():
    art = Image.open(ROOT / 'assets/bossart/perro.jpg').convert('RGB')
    # Original portrait: preserve the game's dog, including its face and suit.
    art = art.crop((115, 165, 530, 910)).resize((310, 556), Image.Resampling.LANCZOS)
    manifest = json.loads((ROOT / 'assets/manifest.json').read_text())['sprites']['perro']
    sheet = Image.open(ROOT / 'assets' / manifest['file']).convert('RGBA')
    fw, fh = manifest['frameW'] * manifest['res'], manifest['frameH'] * manifest['res']
    sprites = [sheet.crop((j * fw, 0, (j + 1) * fw, fh)) for j in range(5)]
    return art, sprites


ART, SPRITES = art_and_sprite()


def label(draw, xy, value, size, fill=WHITE, anchor=None, bold=True):
    draw.text(xy, value, font=FT(size, bold), fill=fill, anchor=anchor,
              stroke_width=1, stroke_fill=INK)


def headphones(im, x, y, scale=1.0):
    """Chunky pixel-art headband and earcups, over the original illustration."""
    d = ImageDraw.Draw(im)
    def rect(box, fill):
        a, b, c, e = box
        d.rectangle((round(x + min(a, c) * scale), round(y + min(b, e) * scale),
                     round(x + max(a, c) * scale), round(y + max(b, e) * scale)), fill=fill)
    for box in [(0, 26, 8, 3), (8, 3, 18, -8), (18, -8, 42, -14),
                (42, -14, 66, -14), (66, -14, 91, -8), (91, -8, 101, 3),
                (101, 3, 109, 28)]:
        rect(box, '#101925')
    for box in [(4, 21, 9, 4), (12, 1, 20, -6), (22, -5, 44, -10),
                (46, -10, 65, -10), (67, -5, 89, -6), (91, 1, 99, 4),
                (102, 6, 105, 23)]:
        rect(box, '#4dc4b4')
    for bx in [(0, 23, 16, 55), (96, 24, 112, 55)]:
        rect(bx, '#101925')
    for bx in [(4, 27, 13, 50), (99, 28, 108, 50)]:
        rect(bx, GOLD)
    rect((7, 31, 10, 46), '#fff0bc')
    rect((102, 32, 105, 46), '#fff0bc')


def frame(i):
    if i == N - 1:
        i = 0  # identical raw image; encoded seam checked separately
    t = i / FPS
    bg = Image.open(ROOT / 'assets/bg/hacienda.png').convert('RGB').resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(9)).convert('RGBA')
    bg.alpha_composite(Image.new('RGBA', (W, H), (8, 15, 27, 218)))
    d = ImageDraw.Draw(bg)
    d.rectangle((48, 116, 491, 121), fill=GOLD)
    label(d, (52, 148), 'LA PLAYLIST DEL PERRO', 27, GOLD)
    label(d, (52, 184), '¿cuál es su nº 1?', 22)
    # Large illustration on the left; use an actual sprite too, as a playable-game signature.
    bob = round(5 * math.sin(t * 14)) if t < 7 or t > 9.3 else 0
    bg.alpha_composite(ART.convert('RGBA'), (33, 251 + bob))
    shade = Image.new('RGBA', (310, 556), (6, 13, 25, 35))
    bg.alpha_composite(shade, (33, 251 + bob))
    headphones(bg, 108, 288 + bob, 1.55)
    pose = (sum(t >= entry[3] for entry in ENTRIES) + (i // 9)) % len(SPRITES)
    sprite = SPRITES[pose].resize((138, 102), Image.Resampling.NEAREST)
    bg.alpha_composite(sprite, (71, 722 + bob))
    d = ImageDraw.Draw(bg)
    # Neutral invented music widget: no borrowed platform chrome, logo or palette.
    d.rounded_rectangle((218, 260, 489, 764), radius=13, fill='#132b37', outline='#4dc4b4', width=3)
    d.rectangle((234, 280, 473, 318), fill='#22434b')
    label(d, (245, 292), 'LISTA / 07', 17, GOLD)
    d.polygon([(446, 288), (446, 309), (461, 299)], fill=GOLD)
    for k, (number, title, duration, start) in enumerate(ENTRIES):
        y = 335 + k * 59
        active = t >= start and t < (ENTRIES[k + 1][3] if k < 5 else 6.28)
        visible = t >= start and (number != '2' or t < start + 8 / FPS)
        d.rectangle((230, y, 477, y + 54), fill='#25505a' if active else '#1a3741',
                    outline='#3d6870', width=1)
        label(d, (237, y + 7), number, 22, GOLD if visible else '#546f70')
        if visible:
            label(d, (268, y + 5), title, 14)
            label(d, (268, y + 27), DETAIL.get(number, ' '), 12, '#9ed8d0', bold=False)
            label(d, (469, y + 36), duration, 12, GOLD, anchor='ra')
        else:
            label(d, (268, y + 10), '················', 14, '#5e8080')
    # The eighth-frame escape: only the number 2 flashes long enough to be decoded.
    if 5.47 + 8 / FPS <= t < REORDER:
        d.rectangle((230, 630, 477, 684), fill='#1a3741')
        label(d, (238, 642), '2', 22, GOLD)
        label(d, (268, 641), '¿lo has visto?', 14, '#9ed8d0')
    y = 335 + 6 * 59
    d.rectangle((230, y, 477, y + 54), fill='#294b4e', outline='#d2b85c', width=2)
    if REVEAL <= t < RETURN:
        if t < REORDER:
            label(d, (239, y + 8), '1', 22, GOLD)
            label(d, (267, y + 5), 'Hoy toca decir', 15, GOLD)
            label(d, (267, y + 27), 'lo contrario', 15, GOLD)
        else:
            # The top track descends to rank 7; the other tracks shift visibly.
            progress = min(1, (t - REORDER) / .55)
            for j, (_, old_title, old_duration, _) in enumerate(ENTRIES):
                yy = round(335 + 59 * j - 20 * (1 - progress))
                d.rectangle((230, yy, 477, yy + 54), fill='#1a3741', outline='#3d6870')
                label(d, (239, yy + 7), str(j + 1), 22, GOLD)
                label(d, (267, yy + 5), old_title, 14)
                label(d, (267, yy + 27), DETAIL.get(ENTRIES[j][0], ' '), 12, '#9ed8d0')
                label(d, (469, yy + 36), old_duration, 12, GOLD, anchor='ra')
            yy = round(335 + 354 * progress)
            d.rectangle((230, yy, 477, yy + 54), fill='#37656b', outline=GOLD, width=2)
            label(d, (239, yy + 8), '7', 22, GOLD)
            label(d, (267, yy + 5), 'Hoy toca decir', 15, GOLD)
            label(d, (267, yy + 27), 'lo contrario', 15, GOLD)
            label(d, (255, 741), '…y mañana, otra', 14, GOLD)
    else:
        label(d, (239, y + 8), '1', 22, GOLD)
        label(d, (270, y + 10), '██████████', 16, GOLD)
    # Reset before the loop; the last frame is explicitly byte-equal to frame zero.
    d.rectangle((53, 833, 490, 836), fill='#4dc4b4')
    label(d, (56, 853), '¿Cuántos hacemos falta?', 15)
    return bg.convert('RGB')


def audio(path):
    """Original square/triangle chiptune, 1-second genre changes, PCM wave."""
    rate = 24000
    motifs = [(196, 2, 4), (261, 3, 5), (330, 5, 2), (147, 4, 3),
              (220, 6, 5), (392, 7, 4), (175, 3, 7)]
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        buf = bytearray()
        for n in range(rate * N // FPS):
            t = n / rate
            if 7.04 <= t < REVEAL or t >= 9.84:
                value = 0
            elif REVEAL <= t < REVEAL + .5:
                phase = t - REVEAL
                value = .35 * math.sin(2 * math.pi * (85 * phase + 48 * phase * phase)) * math.exp(-8 * phase)
            else:
                idx = max(0, sum(t >= entry[3] for entry in ENTRIES))
                base, beat, interval = motifs[idx]
                step = int(t * beat * 3)
                freq = base * (2 ** ([0, interval, 7, 12][step % 4] / 12))
                phase = (t * freq) % 1
                square = 1 if phase < .24 else -1
                triangle = 1 - 4 * abs((t * base / 2) % 1 - .5)
                envelope = max(0, 1 - (t * beat * 3) % 1) ** 2
                value = .13 * square * envelope + .07 * triangle
            buf.extend(struct.pack('<h', max(-32767, min(32767, round(value * 32767)))))
        wav.writeframes(buf)


def main():
    wav = ROOT / 'chf_playlist_perro_audio.wav'
    audio(wav)
    out = ROOT / 'chf_playlist_perro.mp4'
    cmd = ['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', str(wav), '-map', '0:v', '-map', '1:a', '-vf', 'scale=1080:1920:flags=neighbor',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '0', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '160k', '-t', str(N / FPS), '-movflags', '+faststart', str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    samples = []
    try:
        for i in range(N):
            im = frame(i)
            if i in {round(k * (N - 1) / 11) for k in range(12)}:
                samples.append(im.copy())
            proc.stdin.write(im.tobytes())
    finally:
        proc.stdin.close()
    if proc.wait():
        raise RuntimeError('ffmpeg encoding failed')
    wav.unlink()
    sheet = Image.new('RGB', (W * 4, H * 3))
    for j, im in enumerate(samples):
        sheet.paste(im, ((j % 4) * W, (j // 4) * H))
    sheet.resize((1080, 1440)).save(ROOT / 'chf_playlist_perro_12_fotogramas.jpg', quality=90)
    pair = Image.new('RGB', (W * 2, H))
    pair.paste(frame(0), (0, 0))
    pair.paste(frame(N - 1), (W, 0))
    pair.save(ROOT / 'chf_playlist_perro_fotograma_0_vs_ultimo.png')
    edl = {
        'tipo': 'Pieza independiente generada por código; no gameplay',
        'fps': FPS, 'duracion_segundos': N / FPS,
        'cinco_respuestas': {
            'gana': 'Gusto y FOMO: chiste de la semana, listo para mandar.',
            'pregunta_segundo_1': '¿Cuál es el nº 1 de la playlist del Perro?',
            'segunda_vuelta': 'El tema 2 dura ocho fotogramas; el nº 1 baja al 7 y el bucle obliga a releer.',
            'destinatario_y_frase': 'A un amigo que sigue la actualidad: «Mira lo que escucha el Perro».',
            'comentario': '¿Qué tema le falta?'
        },
        'timeline': [
            {'desde': 0, 'hasta': 1.5, 'imagen': 'Pregunta abierta; Perro con cascos y nº 1 tapado.'},
            *({'desde': start, 'hasta': ENTRIES[i + 1][3] if i < 5 else 5.47 + 8 / FPS,
               'imagen': f'{num} · {title} {DETAIL.get(num, "")} · {duration}; cambia el chiptune y la pose.'}
              for i, (num, title, duration, start) in enumerate(ENTRIES)),
            {'desde': 5.47 + 8 / FPS, 'hasta': 7.04, 'imagen': 'Tema 2 se escapa; vuelve a estar ilegible.'},
            {'desde': 7.04, 'hasta': REVEAL, 'audio': 'Silencio de 0,3 s.'},
            {'desde': REVEAL, 'hasta': REORDER, 'imagen': 'Se revela «Hoy toca decir lo contrario».', 'audio': 'Golpe grave original.'},
            {'desde': REORDER, 'hasta': RETURN, 'imagen': 'El nº 1 cae al 7; «…y mañana, otra».'},
            {'desde': RETURN, 'hasta': 10, 'imagen': 'Se vuelve a tapar el nº 1; fotograma final idéntico al inicial.'}
        ],
        'fuentes': ['assets/bossart/perro.jpg', 'assets/sprites/perro@3x.webp', 'index.html ENEMIES.perro / PERRO_FRASES'],
        'audio': 'Síntesis PCM chiptune original por código, sin música de terceros.',
        'propuesta_publicacion': 'El Perro ha compartido su playlist. La nº 1 cambia según el día. Gratis en el navegador: nawebaz.github.io/CHF_GAME #CuantosHacemosFalta #playlist #elecciones #humor #pixelart',
        'publicacion': 'No publicado; pendiente aprobación de Nawe.'
    }
    (ROOT / 'chf_playlist_perro_edl.json').write_text(json.dumps(edl, ensure_ascii=False, indent=2) + '\n')
    print(out, out.stat().st_size, 'raw_loop_equal=', frame(0).tobytes() == frame(N - 1).tobytes())


if __name__ == '__main__':
    main()
