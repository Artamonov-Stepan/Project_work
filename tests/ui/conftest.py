import pytest
from tests.ui.page_objects.login_page import LoginPage

def pytest_addoption(parser):
    parser.addoption(
        "--base_url",
        default="https://www.saucedemo.com",
        help="Base URL for UI tests",
    )

@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base_url")

@pytest.fixture
def login(browser, base_url, wait):
    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)
    login_page.enter_login("standard_user")
    login_page.enter_password("secret_sauce")
    login_page.submit_login()
    assert "/inventory.html" in browser.current_url, "Авторизация не удалась"
    yield browser
