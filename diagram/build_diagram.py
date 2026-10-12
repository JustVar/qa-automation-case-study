"""Build the architecture diagram for the README, in a light and a dark version.

Run from the repo root:

    python diagram/build_diagram.py

It writes diagram/architecture-light.svg and diagram/architecture-dark.svg.
The README shows the one that matches the reader's GitHub theme. Edit the
labels or positions below and run it again. Standard library only.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent
WIDTH = 900
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# Box fills, one per role. White text reads on each in both themes.
FILL = {
    "schedule": "#57606a",
    "suite": "#0969da",
    "core": "#8250df",
    "output": "#1a7f37",
    "notify": "#bc4c00",
}

THEMES = {
    "light": {"group": "#f6f8fa", "group_stroke": "#d0d7de", "label": "#57606a", "line": "#6e7781",
              "text_muted": "#24292f"},
    "dark": {"group": "#161b22", "group_stroke": "#30363d", "label": "#8b949e", "line": "#8b949e",
             "text_muted": "#e6edf3"},
}


def group(x, y, w, h, title, t):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t["group"]}" '
            f'stroke="{t["group_stroke"]}"/>'
            f'<text x="{x + 14}" y="{y + 22}" font-size="13" font-weight="600" '
            f'fill="{t["label"]}" letter-spacing="0.4">{escape(title.upper())}</text>')


def lines_of_text(cx, cy, lines, bold_first=True, color="#ffffff"):
    """Centered text lines; the first is the name, the rest are details."""
    out, n = [], len(lines)
    top = cy - (n - 1) * 9
    for i, line in enumerate(lines):
        weight, size = ("600", 15) if (i == 0 and bold_first) else ("400", 13)
        out.append(f'<text x="{cx}" y="{top + i * 18 + 5}" text-anchor="middle" font-size="{size}" '
                   f'font-weight="{weight}" fill="{color}">{escape(line)}</text>')
    return "".join(out)


def _shape(x, y, w, h, rx, role, lines, archived, t):
    """A filled box, or for a part kept on the archive branch, a dashed outline."""
    if archived:
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="none" '
                f'stroke="{FILL[role]}" stroke-width="2" stroke-dasharray="6 4"/>'
                + lines_of_text(x + w / 2, y + h / 2, lines, color=t["text_muted"]))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{FILL[role]}"/>'
            + lines_of_text(x + w / 2, y + h / 2, lines))


def box(x, y, w, h, role, lines, archived=False, t=None):
    return _shape(x, y, w, h, 8, role, lines, archived, t)


def pill(x, y, w, h, role, lines, archived=False, t=None):
    return _shape(x, y, w, h, h / 2, role, lines, archived, t)


def hexagon(cx, y, w, h, role, lines):
    k = 22
    pts = [(cx - w / 2 + k, y), (cx + w / 2 - k, y), (cx + w / 2, y + h / 2),
           (cx + w / 2 - k, y + h), (cx - w / 2 + k, y + h), (cx - w / 2, y + h / 2)]
    p = " ".join(f"{a},{b}" for a, b in pts)
    return f'<polygon points="{p}" fill="{FILL[role]}"/>' + lines_of_text(cx, y + h / 2, lines)


def cylinder(x, y, w, h, role, lines):
    e = 8  # height of the elliptical cap
    fill = FILL[role]
    body = (f'<path d="M{x},{y + e} L{x},{y + h - e} A{w / 2},{e} 0 0 0 {x + w},{y + h - e} '
            f'L{x + w},{y + e} Z" fill="{fill}"/>')
    top = f'<ellipse cx="{x + w / 2}" cy="{y + e}" rx="{w / 2}" ry="{e}" fill="{fill}" stroke="#ffffff" stroke-opacity="0.45"/>'
    return body + top + lines_of_text(x + w / 2, y + h / 2 + 4, lines)


def path(points, t, dashed=False):
    d = "M" + " L".join(f"{a},{b}" for a, b in points)
    dash = ' stroke-dasharray="5 4"' if dashed else ""
    return (f'<path d="{d}" fill="none" stroke="{t["line"]}" stroke-width="1.6"{dash} '
            f'marker-end="url(#arrow)"/>')


def build(theme: str) -> str:
    t = THEMES[theme]
    parts = []

    # Scheduled runs feed the browser suite only; a person can start either suite.
    parts.append(group(20, 20, 450, 114, "Scheduled runs", t))
    parts.append(pill(40, 54, 200, 60, "schedule", ["Nightly", "Linux lab server"], archived=True, t=t))
    parts.append(pill(250, 54, 200, 60, "schedule", ["Windows runner", "H.265 live video"]))
    parts.append(group(490, 20, 390, 114, "Started by hand", t))
    parts.append(pill(585, 54, 200, 60, "schedule", ["pytest, by hand", "Any suite, any test"]))

    # Test suites.
    parts.append(group(20, 160, 860, 124, "Test suites", t))
    parts.append(box(85, 192, 320, 76, "suite", ["Soterix-WebApp-QA", "Playwright + pytest", "402 browser tests"]))
    parts.append(box(495, 192, 320, 76, "suite", ["Soterix-API-QA", "HTTP requests + pytest", "Internal and partner APIs"]))

    # The shared pipeline at the centre.
    parts.append(hexagon(450, 318, 460, 76, "core", ["SOTERIX-QA-SHARED", "Shared pytest pipeline package"]))

    # Outputs, in three groups.
    gy, gh, gw = 432, 222, 270
    parts.append(group(20, gy, gw, gh, "Reports", t))
    parts.append(group(315, gy, gw, gh, "Test management", t))
    parts.append(group(610, gy, gw, gh, "Records", t))

    parts.append(box(40, gy + 38, 230, 60, "output", ["Run archive", "Run page, health page"]))
    parts.append(box(40, gy + 128, 110, 62, "notify", ["Slack", "Daily summary"], archived=True, t=t))
    parts.append(box(160, gy + 128, 110, 62, "notify", ["Email", "Microsoft 365"]))

    parts.append(box(335, gy + 38, 230, 60, "output", ["QA Touch", "Results read back and checked"]))
    parts.append(box(335, gy + 128, 230, 76, "output", ["Jira bug filer", "Scored on failure history,", "approved by QA, then filed"],
                     archived=True, t=t))

    parts.append(cylinder(650, gy + 34, 190, 70, "output", ["Run record", "Every run"]))
    parts.append(cylinder(650, gy + 124, 190, 70, "output", ["Run ledger", "Armed runs only"]))

    # Arrows: schedule to the browser suite.
    parts.append(path([(140, 114), (140, 150), (205, 150), (205, 190)], t))
    parts.append(path([(350, 114), (350, 150), (285, 150), (285, 190)], t))
    # By hand to the API suite, and a branch to the browser suite.
    parts.append(path([(685, 114), (685, 190)], t))
    parts.append(path([(685, 140), (365, 140), (365, 190)], t))
    # Suites to the pipeline.
    parts.append(path([(245, 268), (245, 300), (395, 300), (395, 316)], t))
    parts.append(path([(655, 268), (655, 300), (505, 300), (505, 316)], t))
    # Pipeline to the three output groups.
    parts.append(f'<path d="M450,394 L450,414 M155,414 L745,414" fill="none" stroke="{t["line"]}" stroke-width="1.6"/>')
    for x in (155, 450, 745):
        parts.append(path([(x, 414), (x, gy - 2)], t))
    # Run archive to Slack and email.
    parts.append(path([(155, gy + 98), (155, gy + 112), (95, gy + 112), (95, gy + 126)], t))
    parts.append(path([(155, gy + 112), (215, gy + 112), (215, gy + 126)], t))

    # Legend for the dashed outlines.
    ly = gy + gh + 22
    parts.append(f'<rect x="20" y="{ly - 12}" width="34" height="16" rx="4" fill="none" '
                 f'stroke="{t["line"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    parts.append(f'<text x="64" y="{ly + 1}" font-size="13" fill="{t["label"]}">Dashed outline: built and '
                 f'used, now kept on the archive/pre-pivot branch</text>')

    height = ly + 18
    defs = (f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
            f'fill="{t["line"]}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
            f'viewBox="0 0 {WIDTH} {height}" font-family="{FONT}" role="img" '
            f'aria-label="A Windows runner and, earlier, a Linux nightly ran the browser suite; a '
            f'person can start either suite. Both run through the shared pytest pipeline, which '
            f'produces the run archive, email reports, the QA Touch upload and run records. The '
            f'nightly, the Slack post and the Jira bug filer are kept on the archive branch.">'
            f'{defs}{"".join(parts)}</svg>\n')


if __name__ == "__main__":
    for name in THEMES:
        target = OUT / f"architecture-{name}.svg"
        target.write_text(build(name), encoding="utf-8")
        print(f"wrote {target}")
