"""Illustrated editorial previews from origin/main sprites; NOT gameplay recordings."""
import json
import math
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parent
OUT=ROOT.parent
W,H,FPS=540,960,24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n:ImageFont.truetype(FONT,n)
MAN=json.loads((ROOT/'assets/manifest.json').read_text())['sprites']
META={x['id']:x for x in json.loads((ROOT/'fichajes.json').read_text())['fichajes']}
ORDER=['tertuliano','cunado','funcionario','abuela','autonomo','currante','agricultor','pluri']
SPEC={
 'tertuliano':('cafe','Café con leche','+velocidad de ataque','EXPERTO EN TODO','Debilita ataque enemigo','grito'),
 'cunado':('tortillaC','Tortilla con cebolla','+daño','0 CONVENCIDOS','Empuja y aturde','golpes'),
 'funcionario':('paella','Paella','+vida','¡VUELVA MAÑANA!','Daña y paraliza','bocadillo'),
 'abuela':('churros','Churros con chocolate','+vida y daño','¿HAS COMIDO?','Cura y lanza zapatilla','grito'),
 'autonomo':('tortillaC','Tortilla con cebolla','+daño','DÍA 30: LA CUOTA','Llama a cuatro refuerzos','golpes'),
 'currante':('tortillaC','Tortilla con cebolla','+daño','SE PARA EL MUNDO','Aturde y potencia aliados','bocadillo'),
 'agricultor':('paella','Paella','+vida','0,20 € → 2,99 €','Tractor en tres carriles','grito'),
 'pluri':('tortillaC','Tortilla con cebolla','+daño','¡3 NÓMINAS!','Llama a dos copias','golpes'),
}
BOSSES={
 'aplazamiento':('EL APLAZAMIENTO','Después de las elecciones','Si la vía baja del 80 %, apenas recibe daño','vias'),
 'coche':('EL COCHE AUTÓNOMO','Modo conducción autónoma activado','Jefe de Puerto Hércules, no de Año de elecciones','puerto'),
}

def spr(key,idx=0):
    a=MAN[key]; im=Image.open(ROOT/'assets'/a['file']).convert('RGBA')
    fw=a['frameW']*a.get('res',1); fh=a['frameH']*a.get('res',1)
    return im.crop((idx*fw,0,(idx+1)*fw,fh))

def paste(im,layer,x,y,width):
    layer=layer.resize((width,round(layer.height*width/layer.width)),Image.Resampling.NEAREST)
    im.paste(layer,(round(x-layer.width/2),round(y-layer.height/2)),layer)

def txt(im,value,y,size=26,col='#f2efe6'):
    d=ImageDraw.Draw(im)
    # Keep editable labels in safe center, with word wrapping.
    import textwrap
    lines=textwrap.wrap(value, width=max(13,int(48*26/size)),break_long_words=False)
    for i,line in enumerate(lines[:3]):
        d.text((W//2,y+i*(size+6)),line,font=F(size),anchor='mm',fill=col,stroke_width=2,stroke_fill='#111823')

def bg(key):
    im=Image.open(ROOT/'assets/bg'/f'{key}.png').convert('RGB').resize((W,H)).filter(ImageFilter.GaussianBlur(7)).convert('RGBA')
    im.alpha_composite(Image.new('RGBA',(W,H),(10,14,24,125)))
    return im

def stamp(im,tag):
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((25,134,514,172),8,fill='#141b25')
    txt(im,tag,153,14,'#ffd34a')
    d.text((32,188),'¿Cuántos hacemos falta?',font=F(17),fill='#f2efe6',stroke_width=1,stroke_fill='#111823')

def character_frame(key,number,n,N):
    if n==N-1:n=0
    item,itemname,effect,label,action,motif=SPEC[key]
    m=META[key]; t=n/FPS
    im=bg('vias'); stamp(im,f'FICHAJE {number:02d}/40 · EVENTO ELECCIONES · 29-N')
    ally=spr(key,(n//5)%5); enemy=spr('recorte',(n//7)%5)
    stage=0 if t<1.65 else 1 if t<3.85 else 2 if t<6.35 else 3 if t<8.5 else 4
    swap=number%2==0
    if stage==0 or stage==4:
        paste(im,ally,270 if number%3 else 224,525,520 if number%3 else 595)
        txt(im,m['grito'].replace(' / ',' '),322,27,'#ffd34a')
        txt(im,'¿A QUIÉN FICHAS?',738,26)
    elif stage in (1,2):
        is_super=(stage==1 and swap) or (stage==2 and not swap)
        paste(im,ally,180 if number%3 else 210,550,385)
        for j,(x,y) in enumerate(((400,470),(439,600),(360,700))):
            paste(im,enemy,x,y,105)
            if is_super and t%0.35<0.18:ImageDraw.Draw(im).ellipse((x-61,y-53,x+61,y+53),outline='#ffd34a',width=6)
        if is_super:
            txt(im,m['super'].upper(),330,28,'#ffd34a')
            txt(im,label,380,25)
            txt(im,action,780,22)
        else:
            txt(im,'ATAQUE BÁSICO',330,25,'#ffd34a')
            txt(im,'GOLPE 1  →  GOLPE 2' if motif=='golpes' else '¿QUÉ CAMBIA DESPUÉS?',760,23)
    else:
        paste(im,ally,165,540,340)
        paste(im,enemy,420,545,145)
        icon=Image.open(ROOT/'assets/icons'/f'{item}@3x.webp').convert('RGBA')
        if t<7.15:
            ImageDraw.Draw(im).rounded_rectangle((82,351,468,695),18,fill='#1e2533',outline='#ffd34a',width=4)
            paste(im,icon,270,469,120)
            txt(im,itemname,568,25,'#ffd34a');txt(im,effect,625,21)
        else:
            txt(im,'MISMO GOLPE · CON OBJETO',350,21,'#ffd34a')
            if motif=='golpes':txt(im,'1 · 2 · ¿3?',730,25)
            elif motif=='bocadillo' and 7.5<t<7.5+8/FPS:txt(im,label,700,25)
            else:txt(im,'¿LO VISTE?',735,25)
    return im.convert('RGB')

def boss_frame(key,n,N):
    if n==N-1:n=0
    name,line,mechanic,setting=BOSSES[key]; t=n/FPS
    im=bg(setting);stamp(im,'JEFE · EVENTO ELECCIONES · 29-N')
    sprite=spr(key,(n//6)%5)
    if t<1.5:
        black=Image.new('RGBA',sprite.size,'#12121b');black.putalpha(sprite.getchannel('A'))
        paste(im,black,270,505,590)
        txt(im,'¿QUÉ TE BLOQUEA?',313,29,'#ffd34a')
    elif t<4:
        paste(im,sprite,270,515,590)
        txt(im,name,303,30,'#ffd34a')
        txt(im,'«'+line+'»',772,24)
    elif t<8.4:
        paste(im,sprite,270+int(math.sin(t*4)*20),510,500)
        txt(im,'¿Y AHORA?',335,26,'#ffd34a')
        txt(im,mechanic,762,20)
        if key=='aplazamiento' and 6<t<7.9:
            ImageDraw.Draw(im).rounded_rectangle((120,695,422,724),9,fill='#421d27')
            ImageDraw.Draw(im).rectangle((127,701,370 if t>7 else 295,718),fill='#ffd34a')
    else:
        paste(im,sprite,270,510,480)
        txt(im,'¿A QUIÉN LLEVARÍAS?',750,24,'#ffd34a')
    return im.convert('RGB')

def output(slug,N,frame,edl):
    out=ROOT/(slug+'.mp4'); samples={round(k*(N-1)/11) for k in range(12)}
    frames=[];first=last=None
    cmd=['ffmpeg','-nostdin','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
         '-f','lavfi','-i','anullsrc=channel_layout=mono:sample_rate=48000', '-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k','-t',str(N/FPS),'-movflags','+faststart',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(N):
            im=frame(i,N)
            if i in samples:frames.append(im.copy())
            if i==0:first=im.copy()
            if i==N-1:last=im.copy()
            p.stdin.write(im.tobytes())
    finally:p.stdin.close()
    if p.wait():raise RuntimeError(f'ffmpeg exited {p.returncode}')
    sheet=Image.new('RGB',(W*4,H*3))
    for j,im in enumerate(frames):sheet.paste(im,(j%4*W,j//4*H))
    sheet.resize((1080,1440)).save(OUT/(slug+'_12_fotogramas.jpg'),quality=88)
    pair=Image.new('RGB',(W*2,H));pair.paste(first,(0,0));pair.paste(last,(W,0))
    pair.save(OUT/(slug+'_fotograma_0_vs_ultimo.png'))
    edl.update(fps=FPS,fotogramas=N,duracion_segundos=N/FPS,
               estado='PREVISUALIZACIÓN ILUSTRADA. Sprites y textos del juego; no es gameplay ni captura del nivel.',
               pendiente='Capturar partida auténtica en el nivel y sustituir recreaciones antes de publicar. Audio en silencio: no hay gritos grabados entre los assets.')
    (OUT/(slug+'_edl.json')).write_text(json.dumps(edl,ensure_ascii=False,indent=2)+'\n')
    print(slug,N,'bucle RGB',first.tobytes()==last.tobytes(),flush=True)

if __name__=='__main__':
    batch=sys.argv[1]
    if batch=='a':
        for num,key in enumerate(ORDER,1):
            m=META[key];item,itemname,effect,label,action,motif=SPEC[key]
            slug=f'chf_fichaje_{num:02d}_{key}'
            output(slug,240,lambda i,N,k=key,j=num:character_frame(k,j,i,N),{
                'cinco_respuestas':{'gana':'Información: habilidad y objeto reales de '+m['nombre'],
                'pregunta_segundo_1':'¿A quién fichas?',
                'segunda_vuelta':{'grito':'grito visual que retorna al inicio','golpes':'recuento de golpes','bocadillo':'bocadillo durante ocho fotogramas'}[motif],
                'destinatario_y_frase':'A quien juega en equipo: «¿A quién ficharías?»',
                'comentario':'¿Fichas a '+m['nombre']+' o esperas al siguiente?'},
                'fuente':['origin/main:index.html TYPES.'+key,'SUPERS.'+key,'ITEMS.'+item,'ACTS Año de elecciones','assets/sprites y bg/vias'],
                'etiqueta':f'FICHAJE {num:02d}/40 · EVENTO ELECCIONES · 29-N',
                'orden': 'súper, ataque, objeto' if num%2==0 else 'ataque, súper, objeto',
                'escenas':[(0,1.65,'sprite y grito textual del juego'),(1.65,3.85,'primer golpe o entrada ilustrada del súper'),(3.85,6.35,'entrada ilustrada del súper o primer golpe'),(6.35,8.5,'objeto y golpe ilustrado con objeto'),(8.5,10,'pregunta y vuelta visual al grito')],
                'objeto':itemname,'efecto':effect,'super':m['super'],'efecto_super':action})
    elif batch=='b':
        for key in BOSSES:
            name,line,mechanic,setting=BOSSES[key]
            slug='chf_jefe_'+key
            output(slug,264,lambda i,N,k=key:boss_frame(k,i,N),{
                'cinco_respuestas':{'gana':'Gusto: presentación del jefe','pregunta_segundo_1':'¿Qué te bloquea?',
                'segunda_vuelta':'línea de jefe y vuelta a silueta','destinatario_y_frase':'A un colega: «¿Cómo lo pararías?»',
                'comentario':'¿A quién llevarías a este jefe?'},
                'fuente':['origin/main:index.html ENEMIES.'+key,'ACTS '+('Año de elecciones' if key=='aplazamiento' else 'Puerto Hércules'),'assets/sprites y bg/'+setting],
                'etiqueta':'JEFE · EVENTO ELECCIONES · 29-N','linea':line,'mecanica':mechanic})
    else:raise ValueError(batch)
