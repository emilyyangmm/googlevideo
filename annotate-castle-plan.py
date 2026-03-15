#!/usr/bin/env python3
"""
古堡平面图标注脚本
"""

from PIL import Image, ImageDraw, ImageFont
import sys

# 打开图片
img_path = sys.argv[1] if len(sys.argv) > 1 else "/Users/emily/.openclaw/media/inbound/castle-plan.jpg"

try:
    img = Image.open(img_path)
except:
    print(f"无法打开图片：{img_path}")
    sys.exit(1)

# 创建绘图对象
draw = ImageDraw.Draw(img)
width, height = img.size

# 字体（使用系统字体）
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", int(height/25))
    font_text = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", int(height/35))
except:
    font_title = ImageFont.load_default()
    font_text = ImageFont.load_default()

# 颜色定义
COLOR_RED = (255, 0, 0, 200)
COLOR_BLUE = (0, 123, 255, 200)
COLOR_GREEN = (40, 167, 69, 200)
COLOR_ORANGE = (255, 193, 7, 200)
COLOR_PURPLE = (111, 66, 193, 200)
COLOR_PINK = (232, 62, 140, 200)
COLOR_CYAN = (0, 200, 200, 200)

# 堡内标注（假设图片是俯视图，上北下南左西右东）
annotations = [
    # 堡内标注
    {"text": "IP 文创零售&游客服务中心", "pos": (width*0.5, height*0.15), "color": COLOR_RED, "area": "堡门入口"},
    {"text": "非遗研学工坊", "pos": (width*0.7, height*0.4), "color": COLOR_BLUE, "area": "东侧核心区"},
    {"text": "国风汉服妆造体验中心", "pos": (width*0.3, height*0.4), "color": COLOR_GREEN, "area": "西侧"},
    {"text": "非遗传承人工作室集群", "pos": (width*0.85, height*0.5), "color": COLOR_ORANGE, "area": "东西两侧"},
    {"text": "岭南茶书房", "pos": (width*0.5, height*0.85), "color": COLOR_PURPLE, "area": "北侧"},
    {"text": "生活美学&摄影工作室", "pos": (width*0.5, height*0.2), "color": COLOR_PINK, "area": "南侧"},
    {"text": "网红打卡景观区", "pos": (width*0.5, height*0.5), "color": COLOR_CYAN, "area": "全堡公共空间"},
    
    # 堡外标注
    {"text": "美食休闲招商区", "pos": (width*0.15, height*0.5), "color": COLOR_RED, "area": "西翼"},
    {"text": "岭南院落精品民宿集群", "pos": (width*0.85, height*0.5), "color": COLOR_BLUE, "area": "东侧"},
    {"text": "护城河滨水休闲景观带", "pos": (width*0.5, height*0.95), "color": COLOR_GREEN, "area": "护城河一圈"},
]

# 绘制标注
for anno in annotations:
    x, y = anno["pos"]
    text = anno["text"]
    color = anno["color"]
    
    # 绘制文本框背景
    bbox = draw.textbbox((0, 0), text, font=font_text)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    padding = 10
    draw.rectangle(
        [x - text_width/2 - padding, y - text_height - padding,
         x + text_width/2 + padding, y + padding],
        fill=(*color[:3], 150)
    )
    
    # 绘制文本
    draw.text((x - text_width/2, y - text_height), text, fill=color, font=font_text)
    
    # 绘制指示线
    draw.line([(x, y), (x, y - 10)], fill=color, width=2)

# 添加图例
legend_y = height * 0.05
legend_items = [
    ("堡内功能区", COLOR_RED),
    ("堡外功能区", COLOR_BLUE),
    ("护城河景观带", COLOR_GREEN),
]

draw.text((20, legend_y), "图例:", fill=(0, 0, 0), font=font_title)
for i, (text, color) in enumerate(legend_items):
    y = legend_y + 30 + i * 25
    draw.rectangle([20, y, 40, y + 15], fill=color)
    draw.text((50, y), text, fill=(0, 0, 0), font=font_text)

# 添加方向指示
draw.text((width - 150, 20), "↑ 北", fill=(255, 0, 0), font=font_title)
draw.text((width - 150, 50), "南↓ (带颜色方向)", fill=(255, 0, 0), font=font_text)

# 保存图片
output_path = "/Users/emily/.openclaw/workspace/castle-plan-annotated.jpg"
img.save(output_path, "JPEG", quality=95)
print(f"✅ 标注完成！已保存到：{output_path}")
