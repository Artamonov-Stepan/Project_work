import allure
from selenium.webdriver.common.by import By
from tests.ui.page_objects.base_page import BasePage


class ProductPage(BasePage):
    PRODUCT_NAME = (By.CLASS_NAME, "inventory_details_name large_size")
    PRODUCT_IMAGE = (By.CLASS_NAME, "inventory_details_img")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_details_price")
    ADD_BUTTON = (By.ID, "add-to-cart")
    REMOVE_BUTTON = (By.ID, "remove")
    BREADCRUMB = (By.ID, "back-to-products")

    @allure.step("Открываю карточку товара 'Sauce Labs Backpack'")
    def open_product_page(self, base_url):
        self.browser.get(f"{base_url}/inventory-item.html?id=4")

    @allure.step("Получаю название товара")
    def get_product_name(self):
        return self.get_element(self.PRODUCT_NAME)

    @allure.step("Проверяю наличие фото товара")
    def product_image(self):
        return self.get_element(self.PRODUCT_IMAGE)

    @allure.step("Получаю цену товара")
    def get_product_price(self):
        price_text = self.get_element(self.PRODUCT_PRICE).text
        return price_text

    @allure.step("Проверяю, что кнопка 'Add to cart' отображается")
    def add_button(self):
        return self.get_element(self.ADD_BUTTON)

    @allure.step("Нажимаю кнопку 'Add to cart'")
    def click_add_to_cart(self):
        self.click(self.ADD_BUTTON)

    @allure.step("Проверяю, что кнопка 'Remove' отображается")
    def remove_button(self):
        return self.get_element(self.REMOVE_BUTTON)

    @allure.step("Нажимаю кнопку 'Remove'")
    def click_remove_from_cart(self):
        self.click(self.REMOVE_BUTTON)

    @allure.step("Возвращаюсь к товарам")
    def back_to_products(self):
        self.click(self.BREADCRUMB)
