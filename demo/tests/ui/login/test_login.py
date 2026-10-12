"""Sign in and out."""
from playwright.sync_api import expect


def test_valid_login_opens_live_view(signed_in):
    """A valid account lands on the live view."""
    expect(signed_in.get_by_role("heading", name="Live view")).to_be_visible()


def test_wrong_password_shows_an_error(page, app_url):
    """A wrong password keeps the user on the sign-in page with an error."""
    page.goto(app_url("login.html"))
    page.fill("#email", "qa@example.com")
    page.fill("#password", "wrong")
    page.click("#signin")
    expect(page.locator("#msg")).to_have_text("Invalid email or password.")


def test_sign_out_returns_to_sign_in(signed_in):
    """Sign out shows the sign-in page."""
    signed_in.click("#logout")
    expect(signed_in.get_by_role("button", name="Sign in")).to_be_visible()
