"""Open the demo run pages in a browser and save the screenshots and the walkthrough frames to shots/.

It hides the run page's date line, so the images carry no date.
"""
import os
import pathlib
import sys
from playwright.sync_api import sync_playwright
runs = pathlib.Path("reports/runs").resolve()
last = sorted(runs.glob("*__tests"))[-1]
out = pathlib.Path("shots"); out.mkdir(exist_ok=True)
frames = []
HIDE_DATE = """() => { const t=document.querySelector('main time, header time, time'); if (t && t.parentElement) t.parentElement.style.display='none'; }"""

def frame(pg, name, hold):
    path = out / f"f{len(frames):02d}-{name}.png"
    pg.screenshot(path=str(path)); frames.append((path, hold))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get("DEMO_CHROMIUM") or None)
    pg = b.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
    pg.goto((last / "run.html").as_uri()); pg.wait_for_timeout(400); pg.evaluate(HIDE_DATE)
    pg.screenshot(path=str(out / "run-overview.png")); frame(pg, "overview", 2600)
    pg.locator('div.row[data-id="4"]').click(); pg.wait_for_timeout(300)
    pg.screenshot(path=str(out / "run-error.png")); frame(pg, "error", 2400)
    pane = pg.locator("#pane")
    pane.get_by_text("Evidence", exact=True).click(); pg.wait_for_timeout(500)
    pg.screenshot(path=str(out / "run-evidence.png")); frame(pg, "evidence", 1600)
    vid = pane.locator("video").first
    if vid.count():
        pg.evaluate("""() => { const v = document.querySelector('#pane video'); let e = v; while (e) { if (e.scrollHeight > e.clientHeight + 4 && getComputedStyle(e).overflowY !== 'visible') { e.scrollTop = v.offsetTop - 120; break; } e = e.parentElement; } }""")
        pg.wait_for_timeout(300)
        vid.evaluate("v => { v.muted = true; v.play(); }")
        for i in range(8):
            pg.wait_for_timeout(450); frame(pg, f"video{i}", 450)
            if i == 5:
                pg.screenshot(path=str(out / "run-video.png"))
    pg.locator('div.row[data-id="6"]').click(); pg.wait_for_timeout(300)
    pane.get_by_text("History", exact=True).click(); pg.wait_for_timeout(400)
    pg.screenshot(path=str(out / "run-history.png")); frame(pg, "history", 2600)
    pg.goto((runs / "health.html").as_uri()); pg.wait_for_timeout(500)
    pg.get_by_role("button", name="Open all").click(); pg.wait_for_timeout(300)
    pg.screenshot(path=str(out / "health.png")); frame(pg, "health", 3000)
    pg.screenshot(path=str(out / "health-full.png"), full_page=True)
    pg.goto((runs / "index.html").as_uri()); pg.wait_for_timeout(500)
    pg.screenshot(path=str(out / "index.png")); frame(pg, "index", 2600)
    b.close()
(out / "frames.txt").write_text("\n".join(f"{p.name} {h}" for p, h in frames))
print(len(frames), "frames")
