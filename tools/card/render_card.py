# -*- coding: utf-8 -*-
"""
render_card.py -- tools/card/social_card.html -> docs/assets/social_card.png (1280x640)

    pip install playwright && playwright install chromium   (one time)
    python tools/card/render_card.py

Fonts load from Google Fonts, so render while online.
"""
import asyncio
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "docs" / "assets" / "social_card.png"


async def main():
    from playwright.async_api import async_playwright
    print("[1/3] launching chromium", flush=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1280, "height": 640})
        print("[2/3] loading social_card.html", flush=True)
        await pg.goto((HERE / "social_card.html").as_uri())
        await pg.evaluate("document.fonts.ready")
        await pg.wait_for_timeout(400)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        await pg.screenshot(path=str(OUT), clip={"x": 0, "y": 0, "width": 1280, "height": 640})
        await b.close()
    print(f"[3/3] wrote {OUT.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
