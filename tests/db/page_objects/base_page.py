import logging
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class BasePage:
    def __init__(self, browser, wait):
        self.browser = browser
        self.wait = wait
        self.__config_logger()

    def __config_logger(self, to_file=False):
        self.logger = logging.getLogger(type(self).__name__)
        os.makedirs("logs", exist_ok=True)
        if to_file:
            self.logger.addHandler(
                logging.FileHandler(f"logs/{self.browser.test_name}.log")
            )
        self.logger.setLevel(level=self.browser.log_level)

    def _text_xpath(self, text):
        xpath_expression = f"//*[text()='{text}']"
        self.logger.debug(f"XPath путь: {xpath_expression}")
        return xpath_expression

    def get_element(self, locator: tuple):
        self.logger.info(f"Получен элемент: {locator}")
        return self.wait.until(EC.visibility_of_element_located(locator))

    def get_elements(self, locator: tuple):
        self.logger.info(f"Получены элементы: {locator}")
        return self.wait.until(EC.visibility_of_all_elements_located(locator))

    def click(self, locator: tuple):
        self.logger.info(f"Кликаем по элементу: {locator}")
        element = self.wait.until(EC.element_to_be_clickable(locator))
        ActionChains(self.browser).move_to_element(element).pause(0.9).click().perform()

    def input_value(self, locator: tuple, text: str):
        self.logger.info(f"Вводим текст '{text}' в элемент: {locator}")
        element = self.get_element(locator)
        element.click()
        element.clear()
        for letter in text:
            element.send_keys(letter)
        self.logger.debug(f"Текст '{text}' успешно введён")

    def is_visible(self, locator: tuple) -> bool:
        try:
            return self.get_element(locator).is_displayed()
        except:
            return False

    def is_clickable(self, locator: tuple) -> bool:
        try:
            self.wait.until(EC.element_to_be_clickable(locator))
            return True
        except:
            return False

    def wait_for_url_to_contain(self, part_url: str, timeout: int = 10):
        self.logger.info(f"Ожидаем, что URL содержит: {part_url}")
        self.wait.until(EC.url_contains(part_url))

    def wait_for_url_to_be(self, full_url: str, timeout: int = 10):
        self.logger.info(f"Ожидаем полный URL: {full_url}")
        self.wait.until(EC.url_to_be(full_url))
