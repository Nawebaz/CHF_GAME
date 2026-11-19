"""Reedit existing recorded T4 footage. No new game actions or footage."""
import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from render_evento import ROOT, OUT, W, H, FPS, output, stamp, txt

RAW=ROOT.parent.parent/'chf-t4/raw'
OLD=ROOT.parent.parent/'chf-t4/out'
CACHE=Path('/home/iceland/.hermes/cache/scratch/chf-t4-v2')
CACHE.mkdir(parents=True,exist_ok=True)
SPEC={
 'debate':('debate','¿A QUIÉN FICHAS?','0 CONVENCIDOS','Cuñao'),
 'promesa':('promesa','¿QUIÉN PAGA EL ALQUILER?','¿Y LA PROMESA?','El Gran Tenedor'),
 'mitin':('mitin','¿CUÁNTOS HICIERON FALTA?','CUÉNTALOS','La cuadrilla'),
 'encuesta':('encuesta','¿QUIÉN GANA AQUÍ?','¿LO VISTE?','Abuela'),
 'mesa':('mesa','¿A QUIÉN LE TOCA?','OTRA VEZ','La mesa'),
 'cierre':('cierre','¿A QUIÉN FICHAS?','¿FALTA ALGUIEN?','La cuadrilla'),
 'dia_despues':('promesa','¿Y AHORA QUÉ?','EL ALQUILER SIGUE','El Gran Tenedor'),
}

def image(key,n):
    if key=='cierre':
        path=CACHE/f'cierre_{n:04d}.jpg'
    else:
        # Same source frames used by the original T4 editing script.
        start={'debate':20,'promesa':150,'mitin':4,'encuesta':25,'mesa':20}[key]
        path=RAW/key/f'f{start+n:04d}.jpg'
        if not path.exists():path=RAW/key/f'f{start:04d}.jpg'
    return Image.open(path).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

def cut(name,i,N):
    if i==N-1:i=0
    source,hook,turn,_=SPEC[name]
    # Use alternating positions in the recording, removing the old stationary end card.
    base=int(i*1.1) if name!='cierre' else min(250,int(i*1.2))
    if name=='dia_despues':base=(220+int(i*.65))%320
    im=image(source,base)
    zoom=1.8 if i<40 else 2.2 if i<115 else 1.9 if i<175 else 2.35
    cx=.52 if i<75 else .46 if i<145 else .57
    cy=.38 if i<100 else .52 if i<170 else .39
    cw,ch=round(W/zoom),round(H/zoom)
    x=max(0,min(W-cw,round(W*cx-cw/2)));y=max(0,min(H-ch,round(H*cy-ch/2)))
    im=im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.Resampling.LANCZOS)
    if i<47:txt(im,hook,320,27,'#ffd34a')
    elif 110<i<118:txt(im,turn,690,25,'#ffd34a')
    elif 158<i<196:txt(im,'¿TÚ QUÉ HARÍAS?',735,24,'#ffd34a')
    stamp(im,'EVENTO ELECCIONES · 29-N')
    return im

if __name__=='__main__':
    selected=sys.argv[1:] or list(SPEC)
    if any(name not in SPEC for name in selected):
        raise ValueError('Unknown clip in '+repr(selected))
    if 'cierre' in selected:
        subprocess.run(['ffmpeg','-nostdin','-loglevel','error','-y','-i',str(OLD/'cierre.mp4'),'-vf','fps=24,scale=540:960','-q:v','4','-start_number','0',str(CACHE/'cierre_%04d.jpg')],check=True)
    for name,(src,hook,turn,hero) in SPEC.items():
        if name not in selected:continue
        slug='v2_'+name
        output(slug,216,lambda i,N,k=name:cut(k,i,N),{
            'cinco_respuestas':{'gana':'Gusto: escena real del juego remontada en primer plano',
               'pregunta_segundo_1':hook,'segunda_vuelta':'bocadillo de 8 fotogramas y repetición de encuadre al final',
               'destinatario_y_frase':'A alguien que juega: «Mira el detalle que se escapa»',
               'comentario':'¿A quién ficharías para esto?'},
            'fuente':['origin/main:index.html y assets','chf-t4/raw/'+src if name!='cierre' else 'chf-t4/out/cierre.mp4'],
            'nota':'Imágenes reales grabadas para tanda 4; montaje y rótulos nuevos. Sin nueva captura de Año de elecciones. Audio silenciado; pendiente sonido de juego y revisión creativa.',
            'escenas':[(0,1.96,'gancho y zoom'),(1.96,4.58,'primer plano del mismo rodaje'),(4.58,4.92,'remate 8 fotogramas'),(4.92,8.96,'pregunta y bucle visual')],
            'personaje_o_elemento':hero})
        edl_path=OUT/(slug+'_edl.json')
        edl=json.loads(edl_path.read_text())
        edl['estado']='Montaje de capturas existentes de la tanda 4; no es una nueva captura del nivel Año de elecciones.'
        edl['pendiente']='Revisión a tamaño móvil, recuperar sonido real y aprobación antes de publicar.'
        edl_path.write_text(json.dumps(edl,ensure_ascii=False,indent=2)+'\n')
