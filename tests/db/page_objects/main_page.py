# main_page.py
import allure
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tests.db.page_objects.base_page import BasePage


class MainPage(BasePage):
    MENU_ITEM_TEMPLATE = "//a[contains(normalize-space(text()), '{}')]"
    CAMERAS_MENU = (
        By.XPATH,
        "//a[@data-bs-toggle='dropdown' and contains(., 'Cameras')]",
    )

    @allure.step("Открываю домашнюю страницу 'Your Store'")
    def open_home_page(self, base_url):
        self.browser.get(f"{base_url}/en-gb?route=common/home")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    @allure.step("Навожу и кликаю по меню 'Cameras'")
    def hover_and_click_cameras_menu(self):
        try:
            element = self.get_element(self.CAMERAS_MENU)
            self.logger.info(
                f"Найден элемент: {element.text}, href: {element.get_attribute('href')}"
            )

            actions = ActionChains(self.browser)
            actions.move_to_element(element).pause(0.5).click().perform()

            self.wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".dropdown-menu.show")
                )
            )
            self.logger.info("Меню 'Cameras' открыто")
        except Exception as e:
            self.logger.error(f"Ошибка при открытии меню 'Cameras': {e}")
            allure.attach(
                self.browser.page_source, "Page Source", allure.attachment_type.HTML
            )
            raise

    @allure.step("Кликаю по пункту меню '{name}'")
    def click_menu_item(self, name):
        locator = (By.XPATH, self.MENU_ITEM_TEMPLATE.format(name))
        self.click(locator)

    @allure.step("Проверяю, что пункт меню '{name}' отображается")
    def is_menu_item_visible(self, name):
        locator = (By.XPATH, self.MENU_ITEM_TEMPLATE.format(name))
        return self.is_clickable(locator)
