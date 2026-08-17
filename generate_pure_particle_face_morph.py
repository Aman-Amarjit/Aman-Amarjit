import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def create_pure_particle_hologram():
    width, height = 400, 400
    n_particles = 1800
    
    # 1. Load portrait
    img_path = "/home/aman-amarjit/Desktop/Aman-Amarjit/avatar.jpg"
    img = Image.open(img_path).convert("L").resize((width, height))
    
    # High-pass filter & edge detection for sharp facial detail
    edges = img.filter(ImageFilter.FIND_EDGES)
    img_np = np.array(img)
    edges_np = np.array(edges)
    
    points_pool = []
    colors_pool = []
    
    # Extract discrete stipple particle coordinates from face photo
    for y in range(12, height - 12, 3):
        for x in range(12, width - 12, 3):
            val = img_np[y, x]
            edge = edges_np[y, x]
            
            # Density sampling: sample features heavily on edges, eyes, hair, and face
            if edge > 35:
                # Strong edge feature (glasses, jawline, hair, eyes)
                points_pool.append((x, y))
                # Cyan/Magenta neon blend based on height
                colors_pool.append((0, 243, 255) if (x + y) % 2 == 0 else (217, 70, 239))
            elif val < 140:
                # Darker facial features (hair, jacket, pupils)
                if random.random() < 0.6:
                    points_pool.append((x, y))
                    colors_pool.append((59, 130, 246) if random.random() < 0.5 else (168, 85, 247))
            elif val < 200:
                # Skin tones / midtones
                if random.random() < 0.25:
                    points_pool.append((x, y))
                    colors_pool.append((0, 243, 255) if random.random() < 0.6 else (16, 185, 129))

    # Ensure exactly n_particles
    if len(points_pool) < n_particles:
        while len(points_pool) < n_particles:
            rx, ry = random.randint(30, 370), random.randint(30, 370)
            points_pool.append((rx, ry))
            colors_pool.append((0, 243, 255))
    else:
        zipped = list(zip(points_pool, colors_pool))
        random.shuffle(zipped)
        zipped = zipped[:n_particles]
        points_pool, colors_pool = zip(*zipped)

    target_face = np.array(points_pool, dtype=float)
    colors_array = np.array(colors_pool)

    # 2. Target 2: Code Brackets </>
    target_code = []
    for i in range(n_particles):
        t = i / float(n_particles)
        if t < 0.33:
            # '<'
            sub_t = t / 0.33
            if sub_t < 0.5:
                cx = 145 - sub_t * 110
                cy = 200 - sub_t * 220
            else:
                cx = 90 + (sub_t - 0.5) * 110
                cy = 90 + (sub_t - 0.5) * 220
        elif t < 0.66:
            # '/'
            sub_t = (t - 0.33) / 0.33
            cx = 225 - sub_t * 50
            cy = 290 - sub_t * 180
        else:
            # '>'
            sub_t = (t - 0.66) / 0.34
            if sub_t < 0.5:
                cx = 255 + sub_t * 110
                cy = 200 - sub_t * 220
            else:
                cx = 310 - (sub_t - 0.5) * 110
                cy = 90 + (sub_t - 0.5) * 220
        target_code.append((cx + random.uniform(-4, 4), cy + random.uniform(-4, 4)))
    target_code = np.array(target_code, dtype=float)

    # 3. Target 3: Pyramid / Triangle
    target_tri = []
    top = (200, 65)
    left_pt = (65, 335)
    right_pt = (335, 335)
    for _ in range(n_particles):
        r1, r2 = random.random(), random.random()
        if r1 + r2 > 1.0:
            r1, r2 = 1.0 - r1, 1.0 - r2
        tx = (1 - r1 - r2) * top[0] + r1 * left_pt[0] + r2 * right_pt[0]
        ty = (1 - r1 - r2) * top[1] + r1 * left_pt[1] + r2 * right_pt[1]
        target_tri.append((tx + random.uniform(-3, 3), ty + random.uniform(-3, 3)))
    target_tri = np.array(target_tri, dtype=float)

    def ease_in_out(t):
        return 0.5 * (1 - math.cos(math.pi * t))

    frames = []
    
    def render_particle_frame(pts, frame_idx):
        canvas = Image.new("RGB", (width, height), (9, 13, 22)) # Pitch Dark Cyberpunk #090d16
        draw = ImageDraw.Draw(canvas)
        
        for idx in range(n_particles):
            px, py = pts[idx]
            # Micro-jitter physics for 3D hologram particle effect
            jx = px + math.sin(frame_idx * 0.15 + idx * 0.1) * 1.0
            jy = py + math.cos(frame_idx * 0.15 + idx * 0.1) * 1.0
            
            c_r, c_g, c_b = colors_array[idx]
            
            # Draw particle dot
            r_dot = 1.2
            draw.ellipse([jx - r_dot, jy - r_dot, jx + r_dot, jy + r_dot], fill=(int(c_r), int(c_g), int(c_b)))
            
        return canvas

    def interpolate_stage(pts_start, pts_end, num_frames):
        stage_frames = []
        for f in range(num_frames):
            alpha = ease_in_out(f / float(num_frames))
            curr_pts = (1 - alpha) * pts_start + alpha * pts_end
            stage_frames.append(render_particle_frame(curr_pts, len(frames) + f))
        return stage_frames

    def hold_stage(pts_static, num_frames):
        stage_frames = []
        for f in range(num_frames):
            stage_frames.append(render_particle_frame(pts_static, len(frames) + f))
        return stage_frames

    # Sequence Timeline
    # 1. Face Particle Hologram Hold (18 frames)
    frames.extend(hold_stage(target_face, 18))
    
    # 2. Morph Face -> Code Brackets (22 frames)
    frames.extend(interpolate_stage(target_face, target_code, 22))
    
    # 3. Code Brackets Hold (14 frames)
    frames.extend(hold_stage(target_code, 14))
    
    # 4. Morph Code -> Pyramid Triangle (22 frames)
    frames.extend(interpolate_stage(target_code, target_tri, 22))
    
    # 5. Pyramid Triangle Hold (14 frames)
    frames.extend(hold_stage(target_tri, 14))
    
    # 6. Morph Pyramid -> Face Particle Hologram (22 frames)
    frames.extend(interpolate_stage(target_tri, target_face, 22))

    # Export high-res GIF
    output_path = "/home/aman-amarjit/Desktop/Aman-Amarjit/profile_particle.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=40, # 25 FPS
        loop=0
    )
    print("Pure particle hologram GIF exported successfully to:", output_path)

if __name__ == "__main__":
    create_pure_particle_hologram()
