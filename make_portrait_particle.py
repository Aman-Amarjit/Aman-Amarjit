"""
Full-Width Particle Morphing System v3
- 600x420px wide card, background #0d1117 (GitHub dark)
- Colors: Electric Hot Pink + Neon Cyan (match profile photo glow)
- Shapes fill the FULL canvas: wide face, sharp triangle apex, wide </>
- Each hold is distinct enough GIF won't deduplicate frames
"""
import random, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

AVATAR  = os.path.join(os.path.dirname(__file__), "avatar.jpg")
OUT_GIF = os.path.join(os.path.dirname(__file__), "portrait_particle.gif")

W, H = 600, 420
BG   = (13, 17, 23)   # #0d1117 — GitHub Dark exact match

# ── Load avatar ───────────────────────────────────────────────────────────────
raw  = Image.open(AVATAR).convert("RGB").resize((W, H), Image.LANCZOS)
raw  = ImageEnhance.Brightness(raw).enhance(3.8)
raw  = ImageEnhance.Contrast(raw).enhance(2.4)
gray = raw.convert("L")
edge = gray.filter(ImageFilter.FIND_EDGES)

px_g = gray.load(); px_e = edge.load(); px_r = raw.load()

# ── Sample face particles ──────────────────────────────────────────────────────
cands, wts = [], []
STEP = 2
for y in range(STEP, H-STEP, STEP):
    for x in range(STEP, W-STEP, STEP):
        v = px_g[x,y]; e = px_e[x,y]
        if v < 22 and e < 12: continue
        w = 0.0
        if   v > 190: w += v * 3.2
        elif v > 120: w += v * 1.8
        elif v >  70: w += v * 1.0
        elif v >  30: w += v * 0.4
        if   e >  24: w += e * 2.2
        elif e >  12: w += e * 1.0
        if w > 8: cands.append((x,y)); wts.append(w)

tw = sum(wts); probs = [w/tw for w in wts]
cum=[]; s=0.0
for p in probs: s+=p; cum.append(s)

def pick():
    r=random.random(); lo,hi=0,len(cum)-1
    while lo<hi:
        m=(lo+hi)//2
        if cum[m]<r: lo=m+1
        else: hi=m
    return lo

random.seed(42)
N = 4200
face_pts=[]; seen=set(); tries=0
while len(face_pts)<N and tries<N*30:
    tries+=1
    x,y = cands[pick()]
    xj=max(2,min(W-2, x+random.randint(-1,1)))
    yj=max(2,min(H-2, y+random.randint(-1,1)))
    k=(xj,yj)
    if k in seen: continue
    seen.add(k)
    ro,go,bo = px_r[x,y]; v=px_g[x,y]
    # Keep the photo's natural dark blue (headphone/monitor) vs pink (face/skin)
    if bo>ro and bo>90:          col=(29, 78, 216)                  # Dark blue glows
    elif v>200:                  col=(255, 200, 240)                 # White-pink highlight
    elif v>140:                  col=(255, 50, 165)                  # Electric hot pink
    elif v>80:                   col=(236, 72, 153)                  # Magenta
    else:                        col=(168, 85, 247)                  # Neon violet
    face_pts.append((xj,yj,col))

Na=len(face_pts)
print(f"Face: {Na} particles on {W}x{H}")

# ── Triangle: tall pointy apex fills height ────────────────────────────────────
random.seed(101)
tri_pts=[]
cx=W//2; top_y=25; bot_y=H-20; half_base=int((bot_y-top_y)*0.72)

for i in range(Na):
    r1=math.sqrt(random.random()); r2=random.random()
    # Vertices: top-center, bottom-left, bottom-right
    ax,ay = cx,        top_y
    bx,by = cx-half_base, bot_y
    dx,dy = cx+half_base, bot_y
    x=(1-r1)*ax + r1*(1-r2)*bx + r1*r2*dx + random.gauss(0,1.5)
    y=(1-r1)*ay + r1*(1-r2)*by + r1*r2*dy + random.gauss(0,1.5)
    t=max(0.0,min(1.0,(y-top_y)/(bot_y-top_y)))
    # Hot pink apex -> dark blue base
    rc=int(255*(1-t) +  29*t)
    gc=int( 50*(1-t) +  78*t)
    bc=int(165*(1-t) + 216*t)
    tri_pts.append((int(max(2,min(W-2,x))), int(max(2,min(H-2,y))), (rc,gc,bc)))

# ── Code Symbol </> wide across full canvas ───────────────────────────────────
random.seed(202)
code_pts=[]
sw=7
third=Na//3; rem=Na-2*third
mid_y=H//2; arm=140
lx=55; rx=W-55; mx=W//2

def make_chevron(n, apex_x, tip_dir, col_fn):
    # tip_dir: +1 = '<' (apex left), -1 = '>' (apex right)
    pts=[]
    open_x = apex_x - tip_dir*110  # open side x
    for i in range(n):
        t=i/n
        if t<0.5:
            tt=t/0.5
            x=int(lerp(open_x, apex_x, tt))+random.randint(-sw,sw)
            y=int(lerp(mid_y-arm, mid_y, tt))+random.randint(-sw,sw)
        else:
            tt=(t-0.5)/0.5
            x=int(lerp(apex_x, open_x, tt))+random.randint(-sw,sw)
            y=int(lerp(mid_y, mid_y+arm, tt))+random.randint(-sw,sw)
        pts.append((max(5,min(W-5,x)), max(5,min(H-5,y)), col_fn(t)))
    return pts

def lerp(a,b,t): return a+(b-a)*t

code_pts = make_chevron(third, lx, 1, lambda t: (255, 50, 165))   # < Electric pink
slash_pts = []
for i in range(third):
    sx = max(5, min(W-5, int(lerp(mx-40, mx+40, i/third)) + random.randint(-sw,sw)))
    sy = max(5, min(H-5, int(lerp(mid_y+arm+20, mid_y-arm-20, i/third)) + random.randint(-sw,sw)))
    slash_pts.append((sx, sy, (37, 99, 235)))
code_pts += slash_pts                                                  # / Dark Blue
code_pts += make_chevron(rem, rx, -1, lambda t: (236, 72, 153))       # > Magenta

# ── Drawing ───────────────────────────────────────────────────────────────────
def dot(d, x, y, r, col):
    g3=max(1,int(r*3.0)); g2=max(1,int(r*1.9))
    d.ellipse([x-g3,y-g3,x+g3,y+g3], fill=tuple(int(c*0.22) for c in col))
    d.ellipse([x-g2,y-g2,x+g2,y+g2], fill=tuple(int(c*0.52) for c in col))
    d.ellipse([x-r, y-r, x+r, y+r],  fill=col)

def ease(t): t=max(0.0,min(1.0,t)); return t*t*(3-2*t)

def lerp_col(c1,c2,t):
    e=ease(t)
    return tuple(max(0,min(255,int(a+(b-a)*e))) for a,b in zip(c1,c2))

def render(pts, r=2):
    img=Image.new("RGB",(W,H),BG); d=ImageDraw.Draw(img)
    for (x,y,col) in pts: dot(d,x,y,r,col)
    return img

def transition(p1,p2,steps=22,ms=32):
    for i in range(steps):
        t=i/steps; et=ease(t)
        cur=[(int(a+(b-a)*et), int(c+(dd-c)*et), lerp_col(ca,cb,t))
             for (a,c,ca),(b,dd,cb) in zip(p1,p2)]
        frames.append(render(cur)); durs.append(ms)

def hold(pts, steps=24, ms=80):
    img=render(pts)
    for _ in range(steps): frames.append(img); durs.append(ms)

print("Rendering animation …")
frames=[]; durs=[]

hold(face_pts, 24, 80)          # Face hold
transition(face_pts, tri_pts)   # → Triangle
hold(tri_pts,  24, 80)          # Triangle hold
transition(tri_pts, code_pts)   # → Code
hold(code_pts, 24, 80)          # Code hold
transition(code_pts, face_pts)  # → Face

print(f"Saving {len(frames)} frames …")
pal=[f.quantize(colors=220,method=Image.Quantize.MEDIANCUT) for f in frames]
pal[0].save(OUT_GIF, save_all=True, append_images=pal[1:],
            loop=0, duration=durs, optimize=False, disposal=2)
print(f"✅  {os.path.getsize(OUT_GIF)//1024} KB  →  {OUT_GIF}")
