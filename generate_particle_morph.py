import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_particle_morph_gif():
    width, height = 400, 400
    n_particles = 1200
    
    # 1. Load portrait and extract high-resolution facial feature particles
    img_path = "/home/aman-amarjit/Desktop/Aman-Amarjit/avatar.jpg"
    img = Image.open(img_path).convert("L").resize((width, height))
    
    # Apply Sobel edge detection to highlight face contour, glasses/eyes, and features
    edges = img.filter(ImageFilter.FIND_EDGES)
    img_np = np.array(img)
    edges_np = np.array(edges)
    
    points_pool = []
    # Sample facial edges and key features
    for y in range(10, height - 10, 2):
        for x in range(10, width - 10, 2):
            edge_val = edges_np[y, x]
            brightness = img_np[y, x]
            
            # High probability for edges (eyes, hair, glasses, face contour)
            if edge_val > 40:
                points_pool.append((x, y))
            elif brightness < 120 and random.random() < 0.3:
                points_pool.append((x, y))
                
    random.shuffle(points_pool)
    
    if len(points_pool) < n_particles:
        while len(points_pool) < n_particles:
            points_pool.append((random.randint(40, 360), random.randint(40, 360)))
            
    target_face = np.array(points_pool[:n_particles], dtype=float)

    # 2. Shape Target 2: Code Brackets </ >
    target_code = []
    # Left bracket '<'
    for t in np.linspace(0, 1, n_particles // 3):
        if t < 0.5:
            x = 130 - t * 110
            y = 200 - t * 220
        else:
            x = 75 + (t - 0.5) * 110
            y = 90 + (t - 0.5) * 220
        target_code.append((x + random.uniform(-3, 3), y + random.uniform(-3, 3)))
        
    # Slash '/'
    for t in np.linspace(0, 1, n_particles // 3):
        x = 220 - t * 40
        y = 290 - t * 180
        target_code.append((x + random.uniform(-3, 3), y + random.uniform(-3, 3)))
        
    # Right bracket '>'
    for t in np.linspace(0, 1, n_particles - len(target_code)):
        if t < 0.5:
            x = 270 + t * 110
            y = 200 - t * 220
        else:
            x = 325 - (t - 0.5) * 110
            y = 90 + (t - 0.5) * 220
        target_code.append((x + random.uniform(-3, 3), y + random.uniform(-3, 3)))
        
    target_code = np.array(target_code, dtype=float)

    # 3. Shape Target 3: Particle Triangle / Pyramid
    target_tri = []
    top = (200, 70)
    left = (70, 330)
    right = (330, 330)
    
    for _ in range(n_particles):
        r1, r2 = random.random(), random.random()
        if r1 + r2 > 1.0:
            r1, r2 = 1.0 - r1, 1.0 - r2
        px = (1 - r1 - r2) * top[0] + r1 * left[0] + r2 * right[0]
        py = (1 - r1 - r2) * top[1] + r1 * left[1] + r2 * right[1]
        target_tri.append((px + random.uniform(-2, 2), py + random.uniform(-2, 2)))
        
    target_tri = np.array(target_tri, dtype=float)

    def ease_in_out(t):
        return 0.5 * (1 - math.cos(math.pi * t))

    frames = []
    hold_frames = 18
    morph_frames = 24
    
    def generate_transition(pts_start, pts_end, is_hold=False):
        for f in range(hold_frames if is_hold else morph_frames):
            alpha = 1.0 if is_hold else ease_in_out(f / float(morph_frames))
            curr_pts = (1 - alpha) * pts_start + alpha * pts_end
            
            canvas = Image.new("RGB", (width, height), (9, 13, 22))
            draw = ImageDraw.Draw(canvas)
            
            for idx, (px, py) in enumerate(curr_pts):
                jx = px + math.sin(f * 0.15 + idx) * 0.8
                jy = py + math.cos(f * 0.15 + idx) * 0.8
                
                ratio = (idx / float(n_particles) + f * 0.015) % 1.0
                r = int(0 * (1 - ratio) + 168 * ratio)
                g = int(243 * (1 - ratio) + 85 * ratio)
                b = int(255 * (1 - ratio) + 247 * ratio)
                
                size = 1.2
                draw.ellipse([jx - size, jy - size, jx + size, jy + size], fill=(r, g, b))
                
            frames.append(canvas)

    generate_transition(target_face, target_face, is_hold=True)
    generate_transition(target_face, target_code, is_hold=False)
    generate_transition(target_code, target_code, is_hold=True)
    generate_transition(target_code, target_tri, is_hold=False)
    generate_transition(target_tri, target_tri, is_hold=True)
    generate_transition(target_tri, target_face, is_hold=False)
    
    output_gif = "/home/aman-amarjit/Desktop/Aman-Amarjit/particle_morphing.gif"
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=40,
        loop=0
    )
    print("High-res 1200-particle morphing GIF successfully generated!")

if __name__ == "__main__":
    create_particle_morph_gif()
