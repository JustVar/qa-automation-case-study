"""Event search."""
from playwright.sync_api import expect


def test_search_all_channels_lists_events(signed_in, app_url):
    """A search over all channels lists every event."""
    signed_in.goto(app_url("events.html"))
    signed_in.click("#search")
    expect(signed_in.locator("#rows tr")).to_have_count(4)


def test_search_by_channel_returns_only_that_channel(signed_in, app_url):
    """Every event a channel filter returns belongs to that channel."""
    signed_in.goto(app_url("events.html"))
    signed_in.select_option("#channel", "Lobby-1")
    signed_in.click("#search")
    channels = signed_in.locator("#rows .ch").all_inner_texts()
    assert channels, "the search returned no events"
    wrong = [c for c in channels if c != "Lobby-1"]
    assert not wrong, f"search for channel 'Lobby-1' returned {len(wrong)} event(s) from {wrong}"
