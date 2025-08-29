from tests.db.page_objects.base_page import BasePage
from selenium.webdriver.common.by import By
import allure


class LoginPage(BasePage):
    LOGIN_FORM = (By.ID, "form-login")
    EMAIL_INPUT = (By.NAME, "email")
    PASSWORD_INPUT = (By.NAME, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    ERROR_MESSAGE = (
        By.XPATH,
        "//*[contains(text(), 'No match for E-Mail Address and/or Password.')]",
    )
    EDIT_ACCOUNT_LINK = (By.LINK_TEXT, "Edit Account")
    FIRST_NAME_INPUT = (By.NAME, "firstname")
    LAST_NAME_INPUT = (By.NAME, "lastname")

    @allure.step("Открываю страницу входа")
    def open_login_page(self, base_url):
        self.browser.get(f"{base_url}/en-gb?route=account/login")
        self.logger.info("Страница входа открыта")

    @allure.step("Проверяю наличие формы входа")
    def is_login_form_present(self):
        form = self.get_element(self.LOGIN_FORM)
        assert form.is_displayed(), "Форма входа не отображается"
        self.logger.info("Форма входа найдена и видима")
        return True

    @allure.step("Ввожу email: {email}")
    def enter_email(self, email):
        self.input_value(self.EMAIL_INPUT, email)

    @allure.step("Ввожу пароль")
    def enter_password(self, password):
        self.input_value(self.PASSWORD_INPUT, password)

    @allure.step("Нажимаю кнопку 'Login'")
    def submit_login(self):
        self.click(self.LOGIN_BUTTON)
        self.logger.info("Кнопка 'Login' нажата")

    @allure.step("Перехожу на страницу редактирования профиля")
    def go_to_edit_account(self):
        self.click(self.EDIT_ACCOUNT_LINK)
        self.logger.info("Переход на страницу редактирования профиля")

    @allure.step("Получаю значение поля 'First Name'")
    def get_first_name_value(self):
        element = self.get_element(self.FIRST_NAME_INPUT)
        value = element.get_attribute("value")
        self.logger.info(f"First Name: {value}")
        return value

    @allure.step("Получаю значение поля 'Last Name'")
    def get_last_name_value(self):
        element = self.get_element(self.LAST_NAME_INPUT)
        value = element.get_attribute("value")
        self.logger.info(f"Last Name: {value}")
        return value

    @allure.step("Проверяю, отображается ли сообщение об ошибке при входе")
    def is_error_message_displayed(self):
        try:
            self.get_element(self.ERROR_MESSAGE)
            return True
        except:
            return False
