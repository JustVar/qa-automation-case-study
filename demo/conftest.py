"""Demo run: made-up tests against a small fictional web app in app/.

DEMO_PHASE picks what the app does in a run, so a series of runs builds a
history: a stream outage, a search regression, an intermittent test.
"""
import getpass
import os
import socket
from pathlib import Path

import pytest

# The run page records the machine and the operator. Fixed names keep the
# screenshots free of whatever machine made them.
socket.gethostname = lambda: "qa-runner-01"
getpass.getuser = lambda: "qa"

pytest_plugins = ["soterix_qa_shared.reporting.run_archive", "soterix_qa_shared.reporting.media"]

APP = "http://localhost:8765"
PHASE = int(os.environ.get("DEMO_PHASE", "1"))


@pytest.fixture
def app_url():
    """The demo app's base URL and the run's phase flags."""
    def url(page_name: str) -> str:
        stall = "1" if PHASE >= 6 else "0"
        leak = "1" if PHASE >= 5 else "0"
        return f"{APP}/{page_name}?stall={stall}&leak={leak}"
    return url


@pytest.fixture
def signed_in(page, app_url):
    """A page signed in to the demo app."""
    page.goto(app_url("login.html"))
    page.fill("#email", "qa@example.com")
    page.fill("#password", "demo-pass")
    page.click("#signin")
    page.wait_for_url("**/live.html*")
    return page


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Use DEMO_CHROMIUM as the browser when it is set; Playwright's own otherwise."""
    path = os.environ.get("DEMO_CHROMIUM")
    return {**browser_type_launch_args, "executable_path": path} if path else browser_type_launch_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """A desktop-sized window, so the videos and screenshots read well."""
    return {**browser_context_args, "viewport": {"width": 1280, "height": 720}}
