# Demo run

The screenshots and the walkthrough on the case study page come from this
folder: 10 made-up browser tests against a small demo web app in `app/`, run
through the same shared pipeline as the real suites. No company system, data
or account is involved.

`DEMO_PHASE` sets what the demo app does in a run, so six runs build a
history:

| Phase | What changes |
|---|---|
| 1, 3 | Everything works |
| 2, 4 | One live-view test fails once (an intermittent failure) |
| 5 | The event search returns an event from another channel |
| 6 | The live video stops, and the search bug stays |

## Run it

You need Python 3.11 or later. The shared package comes from the browser
repo's `vendor/` folder, so clone that repo next to this one.

```bash
git clone https://github.com/JustVar/Soterix-WebApp-QA.git
python -m venv venv
venv/bin/python -m pip install -r Soterix-WebApp-QA/requirements.txt pillow
venv/bin/python -m playwright install chromium
cd qa-automation-case-study/demo
python -m http.server 8765 --bind 127.0.0.1 --directory app &
for phase in 1 2 3 4 5 6; do DEMO_PHASE=$phase ../../venv/bin/python -m pytest; done
../../venv/bin/python -c "from pathlib import Path; from soterix_qa_shared.reporting import health; health.main([], root=Path('.').resolve())"
```

On Windows, use `venv\Scripts\python.exe` and run the six phases one at a
time with `set DEMO_PHASE=1` and so on.

Then open `reports/runs/index.html`, the run archive. Each run has its
`run.html`, and `reports/runs/health.html` is the health page.

To make the images again: `../../venv/bin/python capture.py`, then
`../../venv/bin/python make_gif.py`. Both write to `shots/`. To use a
browser other than Playwright's own, set `DEMO_CHROMIUM` to its path.
