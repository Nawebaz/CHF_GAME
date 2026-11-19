"""Render de pilotos con arte/sfx originales. Escenas reconstruidas, NO captura de motor."""
import json, math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
W,H,FPS = 540,960,24
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
F=lambda n,b=True: ImageFont.truetype(FONT if b else REG,n)
WHITE='#f2efe6'; GOLD='#ffd34a'; RED='#c8202a'
meta=json.loads((ROOT/'fichajes.json').read_text())
config=json.loads((ROOT/'fichaje_plantilla.json').read_text())
tert=next(x for x in meta['fichajes'] if x['id']==config['id'])

def sprite(key,idx=0):
    from PIL import Image
    data=json.loads((ROOT/'assets/manifest.json').read_text())['sprites'][key]
    im=Image.open(ROOT/'assets'/data['file']).convert('RGBA')
    fw=data['frameW']*data['res']; fh=data['frameH']*data['res']
    return im.crop((idx*fw,0,(idx+1)*fw,fh))

def paste_center(im,layer,cx,cy,width):
    ratio=width/layer.width
    layer=layer.resize((width,round(layer.height*ratio)),Image.Resampling.NEAREST)
    im.paste(layer,(int(cx-layer.width/2),int(cy-layer.height/2)),layer)

def text(d,xy,msg,size=29,color=WHITE,anchor='mm'):
    d.text(xy,msg,font=F(size),fill=color,anchor=anchor,stroke_width=2,stroke_fill='#101019')

def base(bg='barrio'):
    im=Image.open(ROOT/f'assets/bg/{bg}.png').convert('RGB').resize((W,H),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(6)).convert('RGBA')
    veil=Image.new('RGBA',(W,H),(9,12,19,105));im.alpha_composite(veil)
    return im

B=base(config['escenario']); boss_bg=base()
T=[sprite(config['id'],i) for i in range(5)]
C=[sprite('tenedor',i) for i in range(5)]
P=sprite('pringao',0); E=sprite(config['enemigo_sprite'],0)
CAFE=Image.open(ROOT/f"assets/icons/{config['objeto']}@3x.webp").convert('RGBA')

def frame_f(i,n):
    if i==n-1: i=0
    t=i/FPS; im=B.copy();d=ImageDraw.Draw(im)
    d.rounded_rectangle((31,132,197,163),radius=10,fill='#101019')
    text(d,(113,147),'FICHAJE '+config['numero'],16,GOLD)
    if t<1.5:
        paste_center(im,T[0],268,495,570)
        grito=tert['grito'] or 'SIN GRITO EN EL JUEGO'
        words=grito.split();mid=(len(words)+1)//2
        d=ImageDraw.Draw(im);text(d,(270,300),' '.join(words[:mid]),31,GOLD);text(d,(270,350),' '.join(words[mid:]),31,GOLD)
        text(d,(270,715),config['pregunta'],23)
    elif t<4:
        # Dos proyectiles reproducidos con el sprite y datos del personaje; no es gameplay.
        paste_center(im,T[3 if int(t*5)%2 else 0],145,550,355)
        paste_center(im,E,425,540,155)
        for k in range(2):
            pulse=max(0,1-abs(t-(2.05+k*1.03))*3)
            x=190+int(215*(1-pulse))
            text(d,(x,492-55*k),config['proyectil_rotulo'],19,GOLD)
        d=ImageDraw.Draw(im)
        text(d,(270,355),f"ATQ BASE {config['ataque_base']} · ÁREA",26,GOLD)
        text(d,(270,729),config['linea_ataque'],22)
    elif t<7:
        paste_center(im,T[0],265,543,430)
        for x,y in [(105,440),(432,490),(398,690)]:paste_center(im,E,x,y,125)
        d=ImageDraw.Draw(im)
        if t<5.1:
            d.rectangle((32,295,508,395),fill='#211b24')
            text(d,(270,325),tert['grito'] or 'SIN GRITO',24,GOLD)
            text(d,(270,366),(tert['super'] or 'SIN SÚPER').upper(),30)
        else:
            for x,y in [(105,440),(432,490),(398,690)]:
                d.ellipse((x-75,y-40,x+75,y+40),outline=GOLD,width=4)
            text(d,(270,792),config['linea_super'],22,GOLD)
    elif t<9.05:
        paste_center(im,T[3 if int((t-7)*6)%2 else 0],192,540,365)
        paste_center(im,E,432,540,135)
        d=ImageDraw.Draw(im)
        if 7.05<=t<7.55: # 12 fotogramas a 24 fps
            d.rounded_rectangle((85,346,465,708),radius=22,fill='#1e2533',outline=GOLD,width=5)
            paste_center(im,CAFE,270,480,110)
            d=ImageDraw.Draw(im);text(d,(270,576),config['objeto_nombre'],29,GOLD)
            text(d,(270,626),config['objeto_efecto'],21)
        else:
            text(d,(270,342),config['ataque_rotulo'],22,GOLD)
            text(d,(360+int(90*math.sin(t*21)),500),config['proyectil_rotulo'],18)
    else:
        paste_center(im,T[0],265,540,475)
        d=ImageDraw.Draw(im);text(d,(270,360),'Y el siguiente dice…',29,GOLD)
        text(d,(270,740),config['pregunta_comentario'],20)
    return im.convert('RGB')

def frame_b(i,n):
    if i==n-1:i=0
    t=i/FPS;im=boss_bg.copy();d=ImageDraw.Draw(im)
    if t<1:
        d.rectangle((0,0,W,H),fill='#741e2a')
        s=C[0].copy();s.putalpha(s.getchannel('A')); black=Image.new('RGBA',s.size,'#090a12');black.putalpha(s.getchannel('A'))
        paste_center(im,black,270,540,570)
        d=ImageDraw.Draw(im);text(d,(270,252),'¿QUIÉN TE SUBE',29,GOLD);text(d,(270,304),'EL ALQUILER?',35,GOLD)
    elif t<3:
        d.rectangle((0,0,W,H),fill='#741e2a')
        for x,y in [(65,535),(460,400),(105,685)]:d.ellipse((x-3,y-3,x+3,y+3),fill=GOLD)
        s=C[0].resize((570,round(C[0].height*570/C[0].width)),Image.Resampling.NEAREST)
        black=Image.new('RGBA',s.size,'#090a12');black.putalpha(s.getchannel('A'))
        reveal=Image.new('RGBA',s.size);cut=int(s.height*(3-t)/2);reveal.paste(s,(0,0));reveal.paste(black.crop((0,0,s.width,cut)),(0,0),black.crop((0,0,s.width,cut)))
        im.paste(reveal,(270-s.width//2,540-s.height//2+int(12*math.sin(t*2))),reveal)
    elif t<5:
        d.rectangle((0,0,W,H),fill='#15131d')
        d.rectangle((22,200,518,760),outline=RED,width=10)
        paste_center(im,C[0],270,445,390)
        d=ImageDraw.Draw(im);text(d,(270,240),'JEFE DE LA FASE',23,RED)
        text(d,(270,681),'EL GRAN TENEDOR',35,GOLD)
        text(d,(270,726),'«¡Sube el alquiler!»',23)
    elif t<9:
        paste_center(im,C[int(t*3)%5],307,472,465)
        for j,(x,y) in enumerate([(110,655),(435,710),(330,762)]):
            paste_center(im,P,x+int(32*math.sin(t*4+j)),y,115)
        d=ImageDraw.Draw(im)
        phase=0 if t<6.15 else 1 if t<7.37 else 2
        names=['SUBE EL ALQUILER','DAÑO EN ÁREA','TRAE INQUILINOS']
        text(d,(270,304),names[phase],29,GOLD)
        if (i%21)<4:d.ellipse((110,445,444,720),outline=RED,width=10)
        if 7.9<t<8.24:
            d.rounded_rectangle((48,166,492,216),radius=10,fill='#24171b')
            d.rectangle((64,189,350,200),fill=RED)
            text(d,(270,243),'JEFE · 1000 PV BASE',17)
    else:
        paste_center(im,C[0],270,442,385)
        for j,x in enumerate([90,180,270,360,450]):paste_center(im,P,x,720+int(10*math.sin(j)),95)
        d=ImageDraw.Draw(im);text(d,(270,304),'¿Cuántos hacemos falta?',30,GOLD)
        if t>10.75:
            mask=Image.new('RGBA',(W,H),(116,30,42,int(255*(t-10.75)/.25)))
            im.alpha_composite(mask)
    return im.convert('RGB')

def render(slug,n,fn,events,edl):
    raw=ROOT/(slug+'.silent.mp4');out=ROOT/(slug+'.mp4')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-', '-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','ultrafast','-qp','0','-pix_fmt','yuv420p',str(raw)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    frames=[];first=None;last=None
    assert proc.stdin is not None
    for i in range(n):
        im=fn(i,n)
        if i in [round(k*(n-1)/11) for k in range(12)]:frames.append(im.copy())
        if i==0:first=im.copy()
        if i==n-1:last=im.copy()
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('ffmpeg video failed')
    assert first is not None and last is not None
    sheet=Image.new('RGB',(540*4,960*3),'#111')
    for j,fr in enumerate(frames):sheet.paste(fr,(j%4*540,j//4*960))
    sheet.resize((1080,1440)).save(ROOT/(slug+'_12_fotogramas.jpg'),quality=88)
    comp=Image.new('RGB',(1080,960));comp.paste(first,(0,0));comp.paste(last,(540,0));comp.save(ROOT/(slug+'_fotograma_0_vs_ultimo.png'))
    inputs=[];filters=[];mix=[]
    for j,(at,sfx) in enumerate(events):
        inputs+=['-i',str(ROOT/'assets/sfx'/('sfx_'+sfx+'.mp3'))]
        filters.append(f'[{j+1}:a]atrim=0:0.5,volume=0.65,adelay={int(at*1000)}|{int(at*1000)}[a{j}]')
        mix.append(f'[a{j}]')
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),*inputs,'-filter_complex',';'.join(filters+[''.join(mix)+f'amix=inputs={len(mix)}:duration=longest:normalize=0[a]']),'-map','0:v','-map','[a]','-t',str(n/FPS),'-c:v','copy','-c:a','aac','-b:a','128k',str(out)],check=True)
    raw.unlink()
    edl['fotogramas']=n;edl['fps']=FPS;edl['duracion_segundos']=n/FPS
    edl['nota_verificacion']='Escenas ilustradas por código con sprites/sfx reales; NO captura del motor. Los golpes y daño mostrado no están verificados en partida. Requiere captura real antes de publicar.'
    (ROOT/(slug+'_edl.json')).write_text(json.dumps(edl,ensure_ascii=False,indent=2)+'\n')
    print(out.name, n, out.stat().st_size,'first-last',first.tobytes()==last.tobytes(),flush=True)

if __name__=='__main__':
    render('chf_fichaje_'+config['id'],240,frame_f,[(0,'shout'),(1.9,'throw_grito'),(3,'throw_grito'),(4.2,'boss'),(5.2,'slam'),(7.65,'ui_card'),(8.1,'throw_grito')],{
      'cinco_respuestas':{'gana':'Información: descubre el ataque en área y la debilidad del súper','pregunta_segundo_1':'¿Qué hace el Tertuliano?','segunda_vuelta':'Carta del café durante 12 fotogramas y frase en bucle','destinatario_y_frase':'Amigo que ve tertulias: «Este es el opinador del juego»','comentario':'¿A quién presentamos mañana?'},
      'fuente':['index.html TYPES.tertuliano, SUPERS.tertuliano, ITEMS.cafe, ITEM_DAMP'],
      'escenas':[{'intervalo':'0–1,5','accion':'sprite y grito originales'},{'intervalo':'1,5–4','accion':'dos impactos ilustrados; ATQ base 6, no lectura de daño en partida'},{'intervalo':'4–7','accion':'Todólogo: debilita ataque enemigo un 25 % durante 3 s'},{'intervalo':'7–9','accion':'Café con leche; desc efectivo +30 % velocidad (40 % antes de ITEM_DAMP)'},{'intervalo':'9–10','accion':'pregunta y costura al primer fotograma'}],
      'zona_segura':'Texto en x=31..508 (a 540); arriba de y=132, debajo de y=792; revisar overlay móvil.'})
    render('chf_jefe_gran_tenedor',264,frame_b,[(1.15,'slam'),(1.9,'slam'),(2.65,'slam'),(3.1,'boss_casero'),(5.15,'slam'),(6.4,'hit'),(7.55,'boss_casero'),(9.2,'slam')],{
      'cinco_respuestas':{'gana':'Gusto: presentación de jefe como tráiler de lucha','pregunta_segundo_1':'¿Quién te sube el alquiler?','segunda_vuelta':'Barra de vida durante 8 fotogramas y relectura del gancho','destinatario_y_frase':'Al colega del alquiler: «Mira al jefe que nos toca»','comentario':'Un número: ¿cuántos hacemos falta?'},
      'fuente':['index.html ENEMIES.casero, bossIntro (elige aleatoriamente una línea), ACTS Barrio; assets/sprites/tenedor@3x.webp'],
      'escenas':[{'intervalo':'0–1','accion':'silueta sobre color del juego'},{'intervalo':'1–3','accion':'revelado progresivo con partículas'},{'intervalo':'3–5','accion':'nombre y línea real posible del intro: «¡Sube el alquiler!»'},{'intervalo':'5–9','accion':'montaje artístico ilustrado: área e inquilinos, NO ataques capturados'},{'intervalo':'9–11','accion':'cuadrilla ilustrada, pregunta y costura'}],
      'zona_segura':'Gancho y nombre centrados; validar último tercio en móvil.'})
