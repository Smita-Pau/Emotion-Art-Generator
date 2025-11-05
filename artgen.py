# artgen.py
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import random
from utils import pick_palette_for_emotions

def generate_art_image(emotions: dict, style="Hybrid (Mandala+Abstract)", complexity=5, color_intensity=6, seed=None, size=(1024,1024)):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    # Watercolor shortcut
    if "Watercolor" in style:
        return generate_watercolor_art(emotions, complexity, color_intensity, size)

    palette = pick_palette_for_emotions(emotions)
    width, height = size
    img = Image.new("RGB", (width, height), palette['background'])
    draw = ImageDraw.Draw(img, 'RGBA')

    dom = max(emotions, key=emotions.get)
    intensity = emotions.get(dom, 0.5)

    if "Mandala" in style:
        _draw_mandala(draw, width, height, palette, complexity, intensity)
    if "Abstract" in style:
        _draw_abstract(draw, width, height, palette, complexity, intensity)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    return img


### ---------------- Mandala Drawing ---------------- ###
def _draw_mandala(draw, w, h, palette, complexity, intensity):
    cx, cy = w//2, h//2
    spokes = int(4 + complexity * 2)
    layers = int(3 + complexity/2)
    max_r = min(cx, cy) * 0.9

    for layer in range(layers):
        r = max_r * (layer+1)/layers
        for s in range(spokes):
            angle = 2*math.pi*s/spokes + (layer*0.1)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)

            size = int(30 * (1 + (complexity/5)) * (1 - layer/layers))
            color = _pick_color_from_palette(palette, layer/layers)
            bbox = [x-size, y-size, x+size, y+size]

            draw.ellipse(bbox, fill=color+(int(180*intensity),), outline=None)


### ---------------- Abstract Blobs ---------------- ###
def _draw_abstract(draw, w, h, palette, complexity, intensity):
    blobs = 3 + complexity//2
    for b in range(blobs):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        max_r = int(min(w,h) * (0.15 + 0.05 * complexity))

        for i in range(10):
            rr = max_r * (1 - i/12) * (0.6 + random.random()*0.8)
            color = _pick_color_from_palette(palette, i/10)

            draw.ellipse([cx-rr, cy-rr, cx+rr, cy+rr],
                         fill=color+(int(160*intensity),), outline=None)


### ---------------- Watercolor Art Mode ---------------- ###
def generate_watercolor_art(emotions, complexity, intensity, size=(1024,1024)):
    palette = pick_palette_for_emotions(emotions)
    emotion_color = tuple(int(palette['colors'][0].lstrip('#')[i:i+2], 16) for i in (0,2,4))

    img_size = size[0]
    img = Image.new("RGB", (img_size, img_size), (255, 255, 255))
    base = img.copy()

    center = img_size // 2
    max_radius = img_size // 3

    for i in range(complexity * 30):
        angle = np.random.uniform(0, 2*np.pi)
        distance = np.random.uniform(0, max_radius)

        x = int(center + distance * np.cos(angle))
        y = int(center + distance * np.sin(angle))

        radius = np.random.randint(30, 110)
        alpha = np.random.randint(40, 160)

        circle = Image.new("RGBA", (radius*2, radius*2), (*emotion_color, 0))
        cdraw = ImageDraw.Draw(circle)
        cdraw.ellipse((0,0,radius*2,radius*2), fill=(*emotion_color, alpha))

        circle = circle.filter(ImageFilter.BoxBlur(10))
        base.paste(circle, (x-radius, y-radius), circle)

    noise = np.random.normal(0, 25, (img_size, img_size, 3)).astype(np.int16)
    paper = np.clip(np.array(base) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(paper).filter(ImageFilter.GaussianBlur(1))

    return img


### ---------------- Palette Helper ---------------- ###
def _pick_color_from_palette(palette, t=0.0):
    colors = palette['colors']
    idx = int(t * (len(colors)-1))
    hexc = colors[idx]
    return tuple(int(hexc.lstrip('#')[i:i+2], 16) for i in (0,2,4))
