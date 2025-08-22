import allure
from selenium.webdriver.common.by import By
from tests.ui.page_objects.base_page import BasePage


class StepOnePage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    CODE = (By.ID, "postal-code")
    CONTINUE = (By.ID, "continue")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div.error-message-container h3")

    @allure.step("Ввожу данные в поле 'First Name'")
    def enter_first_name(self, first_name):
        self.input_value(self.FIRST_NAME, first_name)
        return self

    @allure.step("Ввожу данные в поле 'Last Name'")
    def enter_last_name(self, last_name):
        self.input_value(self.LAST_NAME, last_name)
        return self

    @allure.step("Ввожу данные в поле 'Zip/Postal Code'")
    def enter_code(self, code):
        self.input_value(self.CODE, code)
        return self

    @allure.step("Нажимаю кнопку 'Continue'")
    def click_continue(self):
        self.click(self.CONTINUE)
        allure.attach("Кликнули по кнопке 'Continue'")
        return self

    @allure.step("Получаю текст ошибки на первом шаге")
    def get_error_message(self):
        element = self.get_element(self.ERROR_MESSAGE)
        return element.text.strip()


class StepTwoPage(BasePage):
    FINISH = (By.ID, "finish")

    @allure.step("Нажимаю кнопку 'Finish'")
    def click_finish_checkout(self):
        self.click(self.FINISH)
        allure.attach("Кликнули по кнопке 'Finish'")
        return self


class FinishPage(BasePage):
    COMPLETE_MESSAGE = (By.CLASS_NAME, "complete-header")  # Точнее, чем container
    BACK_HOME = (By.ID, "back-to-products")

    @allure.step("Проверяю, что появилось сообщение 'Thank you for your order!'")
    def is_message_displayed(self):
        try:
            element = self.get_element(self.COMPLETE_MESSAGE)
            return element.is_displayed()
        except:
            return False

    @allure.step("Нажимаю кнопку 'Back Home'")
    def click_back_home_page(self):
        self.click(self.BACK_HOME)
        allure.attach("Кликнули по кнопке 'Back Home'")
        return self
