import allure
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from tests.ui.page_objects.base_page import BasePage


class CartPage(BasePage):
    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_HEADER = (By.CLASS_NAME, "header_secondary_container")
    CHECKOUT = (By.ID, "checkout")

    @allure.step("Открываю страницу 'Корзина'")
    def open_login_page(self, base_url):
        self.browser.get(f"{base_url}/cart.html")
        allure.attach("Открыли страницу 'Корзины'")

    @allure.step("Проверяю, что счётчик корзины отображается")
    def is_cart_counter_displayed(self):
        try:
            element = self.browser.find_element(*self.CART_BADGE)
            if element.is_displayed():
                allure.attach("Счётчик корзины ВИДЕН", name="Состояние счётчика")
                return True
            else:
                return False
        except NoSuchElementException:
            allure.attach("Счётчик корзины НЕ найден в DOM", name="Состояние счётчика")
            return False

    @allure.step("Получаю элемент с количеством товаров в корзине")
    def get_cart_items_count(self):
        return self.get_element(self.CART_BADGE)

    @allure.step("Перехожу в корзину")
    def go_to_cart(self):
        self.click(self.CART_LINK)

    @allure.step("Нажимаю на кнопку 'Checkout'")
    def click_checkout(self):
        self.click(self.CHECKOUT)
