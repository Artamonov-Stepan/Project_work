import allure
from selenium.webdriver.common.by import By
from tests.ui.page_objects.base_page import BasePage


class LoginPage(BasePage):
    TITLE_TEXT = "Swag Labs"
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR_MESSAGE = (By.CSS_SELECTOR, "div.error-message-container h3")

    @allure.step("Открываю страницу 'Логина'")
    def open_login_page(self, base_url):
        self.browser.get(f"{base_url}")
        allure.attach("Открыли страницу 'Регистрации'")

    @allure.step("Ищу заголовок браузера")
    def find_browser_title(self):
        return self.browser.title == self.TITLE_TEXT

    @allure.step("Ищу поле 'Логин'")
    def find_login_field(self):
        return self.get_element(self.USERNAME_INPUT)

    @allure.step("Ввожу данные в поле 'Логин'")
    def enter_login(self, login):
        self.input_value(self.USERNAME_INPUT, login)

    @allure.step("Ищу поле 'Пароль'")
    def find_password_field(self):
        return self.get_element(self.PASSWORD_INPUT)

    @allure.step("Ввожу данные в поле Пароль")
    def enter_password(self, password):
        self.input_value(self.PASSWORD_INPUT, password)

    @allure.step("Нажимаю кнопку 'Login'")
    def submit_login(self):
        self.click(self.LOGIN_BUTTON)
        allure.attach("Кликнули по кнопке 'Login'")

    @allure.step("Получаю текст ошибки авторизации")
    def get_error_message(self):
        element = self.get_element(self.ERROR_MESSAGE)
        return element.text.strip()
