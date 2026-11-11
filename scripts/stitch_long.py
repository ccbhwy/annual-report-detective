# -*- coding: utf-8 -*-
"""按滚动位置拼接整页长图（滚动截屏在页面顶部/底部会有重叠，这里按实际 scrollY 覆盖拼合）"""
from PIL import Image
import os

OUT = r"D:\AI_Project\zuopin\03_发布文案\配图"
PAGE_H = 3070
slices = [(0, "slice_0.png"), (1300, "slice_1300.png"), (1670, "slice_1670.png")]

imgs = [(y, Image.open(os.path.join(OUT, f)).convert("RGB")) for y, f in slices]
W = min(im.width for _, im in imgs)
canvas = Image.new("RGB", (W, PAGE_H), "white")
for y, im in imgs:
    canvas.paste(im.crop((0, 0, W, im.height)), (0, y))

path = os.path.join(OUT, "01_报告整页长图.png")
canvas.save(path, "PNG", optimize=True)
print("stitched:", path, canvas.size, os.path.getsize(path) // 1024, "KB")

# 校验IEND完整
d = open(path, "rb").read()
print("IEND ok:", d[-8:] == b"\x00\x00\x00\x00IEND\xaeB\x60\x82")
