# -*- coding: utf-8 -*-
"""
render_icons.py -- docs/favicon.svg -> favicon.ico + PNG icon set (transparent)

    python tools/render_icons.py      (needs playwright + pillow)
"""
import asyncio, io
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SVG = ROOT / "docs" / "favicon.svg"
A = ROOT / "docs" / "assets"
SIZES = [16, 32, 48, 64, 180, 192, 512]


async def render():
    from playwright.async_api import async_playwright
    svg = SVG.read_text(encoding="utf-8")
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i, s in enumerate(SIZES, 1):
            pg = await b.new_page(viewport={"width": s, "height": s})
            await pg.set_content(f'<html><body style="margin:0;background:transparent">'
                                 f'<div style="width:{s}px;height:{s}px">{svg.replace("<svg ", f"<svg width={s} height={s} ")}</div></body></html>')
            png = await pg.screenshot(omit_background=True, clip={"x": 0, "y": 0, "width": s, "height": s})
            out[s] = Image.open(io.BytesIO(png)).convert("RGBA")
            print(f"[{i}/{len(SIZES)}] rendered {s}px", flush=True)
            await pg.close()
        await b.close()
    return out


def main():
    im = asyncio.run(render())
    A.mkdir(parents=True, exist_ok=True)
    for s in (16, 32, 48, 64):
        im[s].save(A / f"favicon_{s}.png", optimize=True)
    im[64].save(ROOT / "docs" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
                append_images=[im[16], im[32], im[48]])
    # apple-touch: iOS ignores transparency (fills black), so flatten on black explicitly
    bg = Image.new("RGBA", (180, 180), (0, 0, 0, 255)); bg.alpha_composite(im[180])
    bg.convert("RGB").save(A / "apple-touch-icon.png", optimize=True)
    im[192].save(A / "icon_192.png", optimize=True)
    im[512].save(A / "icon_512.png", optimize=True)
    print("[done] favicon.ico (16/32/48/64), favicon_*.png, apple-touch-icon, icon_192/512")


if __name__ == "__main__":
    main()
