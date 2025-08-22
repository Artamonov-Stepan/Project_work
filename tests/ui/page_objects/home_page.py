import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from tests.ui.page_objects.base_page import BasePage


class HomePage(BasePage):
    PRODUCT_CARD = (By.CLASS_NAME, "inventory_item")
    PRODUCT_IMAGE = (By.ID, "item_4_img_link")
    PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
    ADD_BUTTON = (By.ID, "add-to-cart-sauce-labs-backpack")
    REMOVE_BUTTON = (By.ID, "remove-sauce-labs-backpack")
    SHOPPING_CART = (By.ID, "shopping_cart_container")
    FILTER_DROPDOWN = (By.CSS_SELECTOR, "select.product_sort_container")
    AZ_OPTION = (By.XPATH, "//option[@value='az']")
    ZA_OPTION = (By.XPATH, "//option[@value='za']")
    LOHI_OPTION = (By.XPATH, "//option[@value='lohi']")
    HILO_OPTION = (By.XPATH, "//option[@value='hilo']")

    @allure.step("Открываю домашнюю страницу 'Products'")
    def open_home_page(self, base_url):
        self.browser.get(f"{base_url}/inventory.html")

    @allure.step("Проверяю наличие фото товара")
    def product_image_hp(self):
        return self.get_element(self.PRODUCT_IMAGE)

    @allure.step("Получаю цену товара")
    def get_product_price_hp(self):
        price_text = self.get_element(self.PRODUCT_PRICE).text
        return price_text

    @allure.step("Проверяю, что кнопка 'Add to cart' отображается")
    def add_button_hp(self):
        return self.get_element(self.ADD_BUTTON)

    @allure.step("Нажимаю кнопку 'Add to cart'")
    def click_add_to_cart_hp(self):
        self.click(self.ADD_BUTTON)

    @allure.step("Проверяю, что кнопка 'Remove' отображается")
    def remove_button_hp(self):
        return self.get_element(self.REMOVE_BUTTON)

    @allure.step("Нажимаю кнопку 'Remove'")
    def click_remove_from_cart_hp(self):
        self.click(self.REMOVE_BUTTON)

    @allure.step("Нажимаю кнопку переход в корзину")
    def click_shopping_cart(self):
        self.click(self.SHOPPING_CART)

    @allure.step("Ищу все карточки товаров")
    def find_all_product_cards(self):
        return self.get_elements(self.PRODUCT_CARD)

    @allure.step("Ищу первую карточку товара")
    def get_first_product_card(self):
        cards = self.find_all_product_cards()
        if len(cards) > 0:
            return cards[0]
        else:
            raise Exception("No products found on the main page.")

    @allure.step("Ищу последнюю карточку товара")
    def get_last_product_card(self):
        cards = self.find_all_product_cards()
        if len(cards) > 0:
            return cards[-1]
        else:
            raise Exception("No products found on the main page.")

    @allure.step("Получаю название первого товара")
    def get_first_product_name(self):
        return (
            self.get_first_product_card()
            .find_element(By.CLASS_NAME, "inventory_item_name")
            .text
        )

    @allure.step("Получаю название последнего товара")
    def get_last_product_name(self):
        return (
            self.get_last_product_card()
            .find_element(By.CLASS_NAME, "inventory_item_name")
            .text
        )

    @allure.step("Получаю цену первого товара")
    def get_first_product_price(self):
        price_text = (
            self.get_first_product_card()
            .find_element(By.CLASS_NAME, "inventory_item_price")
            .text
        )
        return float(price_text.replace("$", ""))

    @allure.step("Получаю цену последнего товара")
    def get_last_product_price(self):
        price_text = (
            self.get_last_product_card()
            .find_element(By.CLASS_NAME, "inventory_item_price")
            .text
        )
        return float(price_text.replace("$", ""))

    @allure.step("Получаю текущее значение фильтра сортировки")
    def get_sort_value(self):
        select_element = self.get_element(self.FILTER_DROPDOWN)
        return select_element.get_attribute("value")

    @allure.step("Получаю текст активного фильтра")
    def get_sort_text(self):
        try:
            return self.get_element(
                (By.CSS_SELECTOR, "span.active_option[data-test='active-option']")
            ).text
        except:
            select_element = self.get_element(self.FILTER_DROPDOWN)
            return select_element.find_element(By.CSS_SELECTOR, "option[selected]").text

    @allure.step("Меняю сортировку на {value}")
    def change_sorting(self, value):
        select_element = self.wait.until(
            EC.element_to_be_clickable(self.FILTER_DROPDOWN)
        )
        select = Select(select_element)
        select.select_by_value(value)
        self.wait.until(lambda driver: self.get_sort_value() == value)
