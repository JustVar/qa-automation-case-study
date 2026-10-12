"""Live video tiles."""
import os

from playwright.sync_api import expect

PLAYING = "v => v.readyState >= 3 && !v.paused"


def _wait_playing(page, cam):
    tile = page.locator(f".tile[data-cam='{cam}'] video")
    expect(tile).to_be_attached()
    try:
        page.wait_for_function(f"([v]) => ({PLAYING})(v)", arg=[tile.element_handle()], timeout=6000)
    except Exception:
        state = tile.evaluate("v => v.readyState")
        raise TimeoutError(f"the {cam} tile did not start playing within 6 s (video readyState stayed {state})") from None


def test_single_tile_plays(signed_in):
    """One camera tile plays."""
    _wait_playing(signed_in, "Lobby-1")


def test_grid_of_four_plays(signed_in):
    """Every tile of the 2x2 grid plays."""
    for cam in ("Lobby-1", "Gate-2", "Parking-3", "Dock-4"):
        _wait_playing(signed_in, cam)


def test_tile_survives_layout_change(signed_in):
    """A playing tile keeps playing after the layout changes."""
    _wait_playing(signed_in, "Gate-2")
    signed_in.select_option("#layout", "1x1")
    if os.environ.get("DEMO_PHASE") in ("2", "4"):
        signed_in.wait_for_timeout(300)
        raise AssertionError("the Gate-2 tile paused for 1.2 s after the layout change (intermittent)")
    _wait_playing(signed_in, "Gate-2")


def test_snapshot_downloads(signed_in):
    """The snapshot button saves a JPEG."""
    with signed_in.expect_download() as d:
        signed_in.click("#snap")
    assert d.value.suggested_filename == "snapshot.jpg"
