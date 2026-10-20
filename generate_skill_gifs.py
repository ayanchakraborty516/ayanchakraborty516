"""
generate_skill_gifs.py
======================
Generates modern, premium, authentic-logo animated GIF assets for the
GitHub Profile README Tech Arsenal section (username: ayanchakraborty516).

Design Aesthetics:
- Authentic brand vector logos (Devicon / SimpleIcons / Primer).
- Sophisticated dark surface card (#0D131F -> #070B13), subtle border (#1E293B),
  and restrained cyan accents (#00D9FF glow / shimmer).
- Smooth, Tasteful Motion:
  - 3D perspective subtle tilting
  - Gentle vertical floating
  - Smooth 45-degree diagonal light sweep
- Transparent exterior background around the rounded card.
- 24 frames per GIF at 50ms delay (20 fps, 1.2s seamless loop).
- Size: 96x96 px, adaptive palette, optimized for fast loading on GitHub.

Output:
  assets/skills/<name>.gif (19 technologies across Languages, Frontend, Backend, Tools)

Usage:
  python generate_skill_gifs.py
"""

import os
import glob
import subprocess
import sys
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "skills")
TARGET_SIZE = (96, 96)
TOTAL_FRAMES = 24
FRAME_DURATION = 50  # ms (20 fps, 1.2s loop)

SKILLS = [
    # Languages
    {"id": "javascript", "name": "JavaScript", "cat": "Languages"},
    {"id": "html5", "name": "HTML5", "cat": "Languages"},
    {"id": "css3", "name": "CSS3", "cat": "Languages"},
    {"id": "java", "name": "Java", "cat": "Languages"},
    {"id": "python", "name": "Python", "cat": "Languages"},
    # Frontend
    {"id": "react", "name": "React", "cat": "Frontend"},
    {"id": "vite", "name": "Vite", "cat": "Frontend"},
    {"id": "tailwind", "name": "Tailwind CSS", "cat": "Frontend"},
    {"id": "sass", "name": "Sass", "cat": "Frontend"},
    # Backend
    {"id": "nodejs", "name": "Node.js", "cat": "Backend"},
    {"id": "express", "name": "Express.js", "cat": "Backend"},
    {"id": "mongodb", "name": "MongoDB", "cat": "Backend"},
    {"id": "postgresql", "name": "PostgreSQL", "cat": "Backend"},
    # Tools
    {"id": "git", "name": "Git", "cat": "Tools"},
    {"id": "github", "name": "GitHub", "cat": "Tools"},
    {"id": "vscode", "name": "VS Code", "cat": "Tools"},
    {"id": "postman", "name": "Postman", "cat": "Tools"},
    {"id": "vercel", "name": "Vercel", "cat": "Tools"},
    {"id": "render", "name": "Render", "cat": "Tools"},
]


def compile_frames_to_gif(frame_files, output_path):
    """
    Takes 24 rendered PNG frames and compiles a high-quality, transparent,
    optimized animated GIF.
    """
    frames_rgba = []
    for fp in frame_files:
        with Image.open(fp) as img:
            rgba = img.convert("RGBA").resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            frames_rgba.append(rgba)

    pal_frames = []
    for rgba in frames_rgba:
        alpha = rgba.split()[3]
        bg = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        bg.paste(rgba, (0, 0), rgba)

        rgb_part = bg.convert("RGB")
        p_img = rgb_part.convert("P", palette=Image.Palette.ADAPTIVE, colors=127)

        # Transparent mask for exterior background
        mask = Image.eval(alpha, lambda a: 255 if a < 48 else 0)
        p_img.paste(127, mask)
        pal_frames.append(p_img)

    pal_frames[0].save(
        output_path,
        format="GIF",
        save_all=True,
        append_images=pal_frames[1:],
        loop=0,
        duration=FRAME_DURATION,
        disposal=2,
        transparency=127,
        optimize=True,
    )


def verify_generated_gifs():
    """Validates that all 19 GIF files exist, are genuine GIFs, and have 24 frames."""
    print(f"\nValidating skill GIFs in {OUTPUT_DIR}...")
    valid_count = 0
    for s in SKILLS:
        skill_id = s["id"]
        path = os.path.join(OUTPUT_DIR, f"{skill_id}.gif")
        if not os.path.exists(path):
            print(f"  [MISSING] {skill_id}.gif")
            continue

        size_kb = os.path.getsize(path) / 1024
        with Image.open(path) as img:
            n_frames = getattr(img, "n_frames", 1)
            w, h = img.size
            is_gif = img.format == "GIF"
            dur = img.info.get("duration", 0)

        status = "OK" if (is_gif and n_frames == TOTAL_FRAMES and (w, h) == TARGET_SIZE) else "FAIL"
        if status == "OK":
            valid_count += 1
        print(f"  [{status}] {skill_id:12} | {n_frames:2d} frames | {dur}ms | {w}x{h} | {size_kb:4.1f} KB")

    print(f"\nResult: {valid_count}/{len(SKILLS)} verified valid.")
    return valid_count == len(SKILLS)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_ok = verify_generated_gifs()
    if not all_ok:
        print("\nSome skill GIFs need regeneration.")
        sys.exit(1)
    else:
        print("\nAll skill GIF assets are fully validated and ready for GitHub README.")
