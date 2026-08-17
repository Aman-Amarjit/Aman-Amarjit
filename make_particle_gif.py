"""
Particle Morphing GIF v4
- Saves FULL frames (no GIF delta, so shapes are always clear)
- Face particles properly map to bright areas
- </> symbol uses dedicated thick bright strokes
"""
import random, os
from PIL import Image, ImageDraw, ImageFilter

W, H = 400, 400
N    = 2000
BG   = (4, 6, 18)
AVATAR = os.path.join(os.path.dirname(__file__), "avatar.jpg")
OUT    = os.path.join(os.path.dirname(__file__), "profile_particle.gif")

def ease(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)

def lerp(a, b, t): return a + (b-a)*t
def clamp(v, lo, hi): return max(lo, min(hi, v))

def lerp_col(c1, c2, t):
    e = ease(t)
    return tuple(clamp(int(lerp(a,b,e)), 0, 255) for a,b in zip(c1,c2))

def draw_particle(draw, x, y, r, col, br=1.0):
    """3-layer glowing dot"""
    for (radius, frac) in [(r*3.5, 0.15), (r*2, 0.45), (r, 1.0)]:
        radius = max(1, int(radius))
        c = tuple(clamp(int(cc*frac*br), 0, 255) for cc in col)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=c)

# ─── Load & analyse avatar ────────────────────────────────────────────────────
print("Loading avatar …")
raw  = Image.open(AVATAR).convert("RGB").resize((W, H))
gray = raw.convert("L")
edge = gray.filter(ImageFilter.FIND_EDGES)
blur = gray.filter(ImageFilter.GaussianBlur(2))
px_g = gray.load(); px_e = edge.load()
px_r = raw.load();  px_b = blur.load()

# ─── Sample face particles ────────────────────────────────────────────────────
print("Sampling face particles …")
cands, wts = [], []
for y in range(2, H-2, 2):
    for x in range(2, W-2, 2):
        v, e, b = px_g[x,y], px_e[x,y], px_b[x,y]
        if v < 20 and e < 14 and b < 20:
            continue          # pure black background → skip
        w = 0.0
        if v > 155: w += v * 2.5   # monitor/keyboard glow
        elif v > 80: w += v * 1.1
        elif v > 28: w += v * 0.45
        if e > 22: w += e * 1.6    # edges: silhouette, face features
        if w > 9:
            cands.append((x, y))
            wts.append(w)

tw = sum(wts); probs = [w/tw for w in wts]
cum = []; s = 0.0
for p in probs: s += p; cum.append(s)

rng = random.Random(42)
def pick_idx():
    r = rng.random(); lo, hi = 0, len(cum)-1
    while lo < hi:
        mid = (lo+hi)//2
        if cum[mid] < r: lo = mid+1
        else: hi = mid
    return lo

face_pos, face_col = [], []
seen = set()
tries = 0
while len(face_pos) < N and tries < N*30:
    tries += 1
    idx = pick_idx()
    x, y = cands[idx]
    xj = clamp(x + rng.randint(-1,1), 2, W-2)
    yj = clamp(y + rng.randint(-1,1), 2, H-2)
    k = (xj, yj)
    if k in seen: continue
    seen.add(k); face_pos.append((xj,yj))
    ro, go, bo = px_r[x, y]; v = px_g[x, y]
    if v > 155:
        col = (min(255,ro+50), min(255,go+170), 255)
    elif x < W//2:
        col = (min(255,int(ro*0.3)+15), min(255,int(go*0.6)+90), 255)
    else:
        col = (min(255,int(ro*0.55)+110), min(255,int(go*0.2)+15), min(255,int(bo*0.55)+140))
    face_col.append(col)

Na = len(face_pos)
print(f"  → {Na} particles")

# ─── Build </> target ─────────────────────────────────────────────────────────
print("Building </> positions …")
def make_code(n):
    rng2 = random.Random(31)
    pos, col = [], []
    sw = 5
    third = n // 3; rem = n - 2*third
    mid_y = H // 2; arm = 95

    # Widened symbol
    lx = 40;   rx = W - 40;  mx = W // 2

    # '<'
    for i in range(third):
        t = i/third
        if t < 0.5:
            tt = t/0.5
            x = int(lerp(lx+80, lx, tt)) + rng2.randint(-sw,sw)
            y = int(lerp(mid_y-arm, mid_y, tt)) + rng2.randint(-sw,sw)
        else:
            tt = (t-0.5)/0.5
            x = int(lerp(lx, lx+80, tt)) + rng2.randint(-sw,sw)
            y = int(lerp(mid_y, mid_y+arm, tt)) + rng2.randint(-sw,sw)
        pos.append((clamp(x,2,W-2), clamp(y,2,H-2)))
        col.append((0, 230, 255))
    # '/'
    for i in range(third):
        t = i/third
        x = int(lerp(mx-30, mx+30, t)) + rng2.randint(-sw,sw)
        y = int(lerp(mid_y+arm+15, mid_y-arm-15, t)) + rng2.randint(-sw,sw)
        pos.append((clamp(x,2,W-2), clamp(y,2,H-2)))
        col.append((210, 215, 255))
    # '>'
    for i in range(rem):
        t = i/rem
        if t < 0.5:
            tt = t/0.5
            x = int(lerp(rx-80, rx, tt)) + rng2.randint(-sw,sw)
            y = int(lerp(mid_y-arm, mid_y, tt)) + rng2.randint(-sw,sw)
        else:
            tt = (t-0.5)/0.5
            x = int(lerp(rx, rx-80, tt)) + rng2.randint(-sw,sw)
            y = int(lerp(mid_y, mid_y+arm, tt)) + rng2.randint(-sw,sw)
        pos.append((clamp(x,2,W-2), clamp(y,2,H-2)))
        col.append((210, 55, 235))
    return pos, col

code_pos, code_col = make_code(Na)

rng3 = random.Random(99)
chaos_pos = [(rng3.randint(5,W-5), rng3.randint(5,H-5)) for _ in range(Na)]

# ─── Render ───────────────────────────────────────────────────────────────────
def interp_p(src, dst, t):
    e = ease(t)
    return [(clamp(int(lerp(sx,dx,e)),1,W-1), clamp(int(lerp(sy,dy,e)),1,H-1))
            for (sx,sy),(dx,dy) in zip(src,dst)]

def interp_c(sc, dc, t):
    return [lerp_col(a,b,t) for a,b in zip(sc,dc)]

def render(positions, colors, br=1.0):
    img = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(img)
    for (x,y), c in zip(positions, colors):
        draw_particle(d, x, y, 2, c, br)
    return img

frames, durs = [], []
HOLD = 20; MOVE = 22; CHAOS = 6

print("Rendering frames …")
dim_col = [(20, 55, 180)]*Na

for _ in range(HOLD):   frames.append(render(face_pos, face_col));          durs.append(80)
for i in range(MOVE):
    t = i/MOVE
    frames.append(render(interp_p(face_pos, chaos_pos, t), interp_c(face_col, dim_col, t))); durs.append(28)
for _ in range(CHAOS):  frames.append(render(chaos_pos, dim_col, 0.45));    durs.append(30)
for i in range(MOVE):
    t = i/MOVE
    frames.append(render(interp_p(chaos_pos, code_pos, t), interp_c(dim_col, code_col, t))); durs.append(28)
for _ in range(HOLD):   frames.append(render(code_pos, code_col));           durs.append(80)
for i in range(MOVE):
    t = i/MOVE
    frames.append(render(interp_p(code_pos, face_pos, t), interp_c(code_col, face_col, t))); durs.append(28)

print(f"Saving {len(frames)} frames (full-frame, no delta optimization) …")

# KEY FIX: Convert to RGB explicitly then palette — disable disposal for full frames
rgb_frames = frames  # already RGB

# Save as non-optimized (full frames shown each time)
# Use disposal=2 (restore background) so each frame is drawn fresh
pal_frames = []
for f in rgb_frames:
    pf = f.quantize(colors=220, method=Image.Quantize.MEDIANCUT)
    pal_frames.append(pf)

pal_frames[0].save(
    OUT,
    save_all=True,
    append_images=pal_frames[1:],
    loop=0,
    duration=durs,
    optimize=False,
    disposal=2,    # ← CRITICAL: restore-to-background before each frame
)
print(f"✅  Done!  {os.path.getsize(OUT)//1024} KB")
