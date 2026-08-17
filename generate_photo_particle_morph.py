import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

def create_photo_particle_morph():
    img_path = "/home/aman-amarjit/Desktop/Aman-Amarjit/avatar.jpg"
    base_img = Image.open(img_path).convert("RGB").resize((400, 400))
    base_np = np.array(base_img)
    
    width, height = 400, 400
    
    # Extract dense pixel grid from real photo
    step = 5
    particles = []
    for y in range(0, height, step):
        for x in range(0, width, step):
            r, g, b = base_np[y, x]
            particles.append({
                'orig_x': x,
                'orig_y': y,
                'color': (r, g, b)
            })
            
    n_particles = len(particles)
    
    # Target 2: Code Brackets </>
    target_code = []
    for i in range(n_particles):
        t = i / float(n_particles)
        if t < 0.33:
            # '<'
            sub_t = t / 0.33
            if sub_t < 0.5:
                cx = 140 - sub_t * 100
                cy = 200 - sub_t * 200
            else:
                cx = 90 + (sub_t - 0.5) * 100
                cy = 100 + (sub_t - 0.5) * 200
        elif t < 0.66:
            # '/'
            sub_t = (t - 0.33) / 0.33
            cx = 220 - sub_t * 40
            cy = 290 - sub_t * 180
        else:
            # '>'
            sub_t = (t - 0.66) / 0.34
            if sub_t < 0.5:
                cx = 260 + sub_t * 100
                cy = 200 - sub_t * 200
            else:
                cx = 310 - (sub_t - 0.5) * 100
                cy = 100 + (sub_t - 0.5) * 200
        target_code.append((cx + random.uniform(-4, 4), cy + random.uniform(-4, 4)))
        
    # Target 3: Pyramid / Triangle
    target_tri = []
    top = (200, 70)
    left_pt = (70, 330)
    right_pt = (330, 330)
    for _ in range(n_particles):
        r1, r2 = random.random(), random.random()
        if r1 + r2 > 1.0:
            r1, r2 = 1.0 - r1, 1.0 - r2
        tx = (1 - r1 - r2) * top[0] + r1 * left_pt[0] + r2 * right_pt[0]
        ty = (1 - r1 - r2) * top[1] + r1 * left_pt[1] + r2 * right_pt[1]
        target_tri.append((tx + random.uniform(-3, 3), ty + random.uniform(-3, 3)))

    def ease_in_out(t):
        return 0.5 * (1 - math.cos(math.pi * t))

    frames = []
    
    # Sequence:
    # 1. Real Photo Hold (15 frames)
    # 2. Photo Disintegrates to Code Particles (20 frames)
    # 3. Code Hold (12 frames)
    # 4. Code Morphs to Pyramid Triangle (20 frames)
    # 5. Triangle Hold (12 frames)
    # 6. Triangle Assembles back into Real Photo (20 frames)

    # Frame generator helper
    def render_photo_frame(blend_to_particles_alpha=0.0):
        # Blend base image with glowing particle overlay
        frame = base_img.copy()
        if blend_to_particles_alpha > 0:
            # Fade base photo out
            enhancer = ImageEnhance.Brightness(frame)
            frame = enhancer.enhance(1.0 - blend_to_particles_alpha)
            
            # Overlay exploding particles
            draw = ImageDraw.Draw(frame)
            for idx, p in enumerate(particles):
                ox, oy = p['orig_x'], p['orig_y']
                # Disperse outward from center
                dx = (ox - 200) * (blend_to_particles_alpha * 0.8)
                dy = (oy - 200) * (blend_to_particles_alpha * 0.8)
                
                cur_x = ox + dx + math.sin(idx + blend_to_particles_alpha * 5) * 3
                cur_y = oy + dy + math.cos(idx + blend_to_particles_alpha * 5) * 3
                
                # Neon glow tint
                c_r, c_g, c_b = p['color']
                glow_r = int(c_r * (1 - blend_to_particles_alpha) + 0 * blend_to_particles_alpha)
                glow_g = int(c_g * (1 - blend_to_particles_alpha) + 243 * blend_to_particles_alpha)
                glow_b = int(c_b * (1 - blend_to_particles_alpha) + 255 * blend_to_particles_alpha)
                
                draw.ellipse([cur_x - 1.5, cur_y - 1.5, cur_x + 1.5, cur_y + 1.5], fill=(glow_r, glow_g, glow_b))
        return frame

    def render_morph_stage(pts_start, pts_end, steps):
        stage_frames = []
        for f in range(steps):
            t = ease_in_out(f / float(steps))
            canvas = Image.new("RGB", (width, height), (9, 13, 22))
            draw = ImageDraw.Draw(canvas)
            
            for idx in range(n_particles):
                p = particles[idx]
                s_x, s_y = pts_start[idx]
                e_x, e_y = pts_end[idx]
                
                cur_x = (1 - t) * s_x + t * e_x + math.sin(f * 0.2 + idx) * 1.0
                cur_y = (1 - t) * s_y + t * e_y + math.cos(f * 0.2 + idx) * 1.0
                
                # Particle color mix (Cyan #00F3FF & Purple #9D00FF)
                ratio = (idx / float(n_particles) + f * 0.02) % 1.0
                r = int(0 * (1 - ratio) + 157 * ratio)
                g = int(243 * (1 - ratio) + 0 * ratio)
                b = int(255 * (1 - ratio) + 255 * ratio)
                
                draw.ellipse([cur_x - 1.5, cur_y - 1.5, cur_x + 1.5, cur_y + 1.5], fill=(r, g, b))
            stage_frames.append(canvas)
        return stage_frames

    # Build full animation sequence
    # 1. Hold Real Photo
    for _ in range(12):
        frames.append(base_img.copy())
        
    # 2. Photo Disintegrates
    for f in range(15):
        alpha = ease_in_out(f / 15.0)
        frames.append(render_photo_frame(alpha))
        
    # 3. Morph Dispersed Photo to Code Brackets
    photo_pts = [(p['orig_x'], p['orig_y']) for p in particles]
    frames.extend(render_morph_stage(photo_pts, target_code, steps=20))
    
    # 4. Hold Code
    code_hold = render_morph_stage(target_code, target_code, steps=10)
    frames.extend(code_hold)
    
    # 5. Morph Code to Triangle
    frames.extend(render_morph_stage(target_code, target_tri, steps=20))
    
    # 6. Hold Triangle
    tri_hold = render_morph_stage(target_tri, target_tri, steps=10)
    frames.extend(tri_hold)
    
    # 7. Re-assemble Triangle back into Real Photo
    frames.extend(render_morph_stage(target_tri, photo_pts, steps=20))
    
    # Save output GIF
    output_path = "/home/aman-amarjit/Desktop/Aman-Amarjit/profile_particle.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=45,
        loop=0
    )
    print("Photo particle morphing animation generated successfully at:", output_path)

if __name__ == "__main__":
    create_photo_particle_morph()
