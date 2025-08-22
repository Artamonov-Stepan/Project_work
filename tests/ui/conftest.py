import pytest
import logging
import allure
import json
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from tests.ui.page_objects.login_page import LoginPage


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        required=True,
        help="Browser to run tests (chrome, firefox)",
        choices=["chrome", "ch", "firefox", "ff"],
    )
    parser.addoption(
        "--headless", action="store_true", help="Run browser in headless mode"
    )
    parser.addoption(
        "--base_url", help="Base application URL", default="https://www.saucedemo.com"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.outcome != "passed":
        driver = getattr(item, "_driver", None)
        if driver is not None:
            screenshot_path = os.path.join(
                os.getcwd(), "screenshots", f"{item.name}_failure.png"
            )
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            driver.get_screenshot_as_file(screenshot_path)
            allure.attach.file(
                screenshot_path,
                name="Failure Screenshot",
                attachment_type=allure.attachment_type.PNG,
            )


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base_url")


@pytest.fixture
def wait(browser):
    return WebDriverWait(browser, 10)


@pytest.fixture(scope="function")
def browser(request):
    browser_name = request.config.getoption("--browser").lower()
    headless = request.config.getoption("--headless")

    driver = None

    if browser_name in ["ch", "chrome"]:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
    elif browser_name in ["ff", "firefox"]:
        options = FFOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options
        )
    else:
        raise pytest.UsageError(
            f"Unsupported browser: {browser_name}. Supported: chrome, firefox"
        )

    request.node._driver = driver

    logging.info(f"Starting test: {request.node.name}")

    allure.attach(
        name=driver.session_id,
        body=json.dumps(driver.capabilities, indent=4, ensure_ascii=False),
        attachment_type=allure.attachment_type.JSON,
    )

    driver.test_name = request.node.name
    driver.log_level = logging.WARNING

    yield driver

    driver.quit()


@pytest.fixture
def login(browser, base_url, wait):
    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)
    login_page.enter_login("standard_user")
    login_page.enter_password("secret_sauce")
    login_page.submit_login()
    assert "/inventory.html" in browser.current_url, "Авторизация не удалась"
    yield browser
