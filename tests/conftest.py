import pytest
import logging
import allure
import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        default="firefox",
        choices=["chrome", "ch", "firefox", "ff"],
        help="Browser to run tests (default: firefox)",
    )
    parser.addoption(
        "--headless", action="store_true", help="Run browser in headless mode"
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


@pytest.fixture(scope="function")
def browser(request):
    browser_name = request.config.getoption("--browser").lower()
    # headless = request.config.getoption("--headless")
    headless = True

    if not headless:
        headless = True

    driver = None
    if browser_name in ["ch", "chrome"]:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
    elif browser_name in ["ff", "firefox"]:
        options = FFOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()), options=options
        )
    else:
        raise pytest.UsageError(
            f"Unsupported browser: {browser_name}. Supported: chrome, firefox"
        )

    request.node._driver = driver
    logging.info(f"Starting test: {request.node.name} on {browser_name.upper()}")

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
def wait(browser):
    return WebDriverWait(browser, 10)


# pytest tests/ --alluredir=./allure-results Для фиксации
# allure serve ./allure-results - просмотр отчёта об прохождении тестов в ui формате
