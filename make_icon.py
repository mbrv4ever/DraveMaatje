# DraveMaatje - eigen icoon: een vrolijk rond maatje met een hartje (Pillow -> geldige .ico)
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "assets"), exist_ok=True)
S = 512
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((16, 16, S - 16, S - 16), radius=110, fill=(22, 19, 31, 255), outline=(127, 119, 221, 255), width=18)
# rond gezichtje
d.ellipse((96, 86, 416, 406), fill=(94, 224, 200, 255), outline=(240, 236, 255, 255), width=12)
d.ellipse((176, 190, 216, 238), fill=(22, 19, 31, 255))                 # ogen
d.ellipse((296, 190, 336, 238), fill=(22, 19, 31, 255))
d.ellipse((186, 198, 200, 212), fill=(255, 255, 255, 255))
d.ellipse((306, 198, 320, 212), fill=(255, 255, 255, 255))
d.arc((176, 230, 336, 340), start=20, end=160, fill=(22, 19, 31, 255), width=16)   # lach
d.ellipse((140, 262, 176, 286), fill=(255, 150, 170, 200))              # blosjes
d.ellipse((336, 262, 372, 286), fill=(255, 150, 170, 200))
# hartje rechtsonder
hx, hy = 392, 392
d.ellipse((hx - 56, hy - 44, hx, hy + 8), fill=(255, 110, 140, 255))
d.ellipse((hx - 8, hy - 44, hx + 48, hy + 8), fill=(255, 110, 140, 255))
d.polygon([(hx - 54, hy - 6), (hx + 46, hy - 6), (hx - 4, hy + 60)], fill=(255, 110, 140, 255))
im.resize((256, 256), Image.LANCZOS).save(os.path.join(HERE, "assets", "icon_256.png"))
im.save(os.path.join(HERE, "assets", "icon.ico"), format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icoon klaar")
