"""Join the frames capture.py saved into shots/walkthrough.gif. Needs Pillow."""
from pathlib import Path

from PIL import Image

shots = Path("shots")
frames, holds = [], []
for line in (shots / "frames.txt").read_text().splitlines():
    name, hold = line.split()
    im = Image.open(shots / name).convert("RGB")
    im = im.resize((1080, int(im.height * 1080 / im.width)), Image.LANCZOS)
    frames.append(im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
    holds.append(int(hold))
frames[0].save(shots / "walkthrough.gif", save_all=True, append_images=frames[1:], duration=holds, loop=0, optimize=True)
print(f"wrote {shots / 'walkthrough.gif'}")
