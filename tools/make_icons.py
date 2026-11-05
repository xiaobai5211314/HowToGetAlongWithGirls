#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《如何与女生相处》专属 Claude UI 高清品牌图标资产"""

from PIL import Image, ImageDraw
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def create_brand_icon(size=180, radius=42):
    scale = 4
    s = size * scale
    r = radius * scale
    
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制 Claude 标志性陶土红背景圆角矩形
    brand_color = (201, 100, 66, 255) # #c96442
    draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=r, fill=brand_color)
    
    # 绘制两性相处与心动对话微标（爱心与气泡结合）
    # 大气泡底座
    bw = int(s * 0.54)
    bh = int(s * 0.38)
    bx = int((s - bw) / 2)
    by = int(s * 0.26)
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(r * 0.45), fill=(255, 255, 255, 255))
    
    # 对话气泡小尾巴
    tail_pts = [
        (bx + int(bw * 0.32), by + bh - 2),
        (bx + int(bw * 0.16), by + bh + int(s * 0.11)),
        (bx + int(bw * 0.46), by + bh - 2)
    ]
    draw.polygon(tail_pts, fill=(255, 255, 255, 255))
    
    # 气泡内部心形图案 (绘制红色心动小徽标)
    # 心形数学参数方程绘制
    cx = bx + int(bw / 2)
    cy = by + int(bh / 2)
    heart_scale = s * 0.009
    
    import math
    heart_pts = []
    for t in [i * 0.05 for i in range(126)]:
        x = 16 * (math.sin(t) ** 3)
        y = -(13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        px = cx + int(x * heart_scale)
        py = cy + int(y * heart_scale) - int(s * 0.01)
        heart_pts.append((px, py))
    
    if len(heart_pts) > 2:
        draw.polygon(heart_pts, fill=brand_color)
    
    # 下采样抗锯齿
    img_out = img.resize((size, size), Image.Resampling.LANCZOS)
    return img_out

def main():
    # 1. apple-touch-icon.png (180x180)
    icon_180 = create_brand_icon(180, 42)
    icon_180.save(ROOT / 'apple-touch-icon.png', 'PNG')
    print("Saved apple-touch-icon.png")
    
    # 2. logo.png (128x128)
    logo_128 = create_brand_icon(128, 30)
    logo_128.save(ROOT / 'logo.png', 'PNG')
    print("Saved logo.png")
    
    # 3. favicon.ico (包含 16, 32, 48 尺寸)
    icon_48 = create_brand_icon(48, 12)
    icon_32 = create_brand_icon(32, 8)
    icon_16 = create_brand_icon(16, 4)
    icon_48.save(
        ROOT / 'favicon.ico',
        format='ICO',
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[icon_32, icon_16]
    )
    print("Saved favicon.ico")

if __name__ == '__main__':
    main()
