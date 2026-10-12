"""User administration."""
from playwright.sync_api import expect


def test_add_and_remove_user(signed_in, app_url):
    """A new user appears in the list, then is removed, and the count returns."""
    signed_in.goto(app_url("admin.html"))
    rows = signed_in.locator("#users tr")
    before = rows.count()
    signed_in.fill("#newuser", "new.user@example.com")
    signed_in.click("#add")
    expect(rows).to_have_count(before + 1)
    signed_in.locator("#users tr", has_text="new.user@example.com").get_by_role("button", name="Remove").click()
    expect(rows).to_have_count(before)
