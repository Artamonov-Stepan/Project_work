from tests.ui.page_objects.login_page import LoginPage
from tests.ui.page_objects.product_page import ProductPage
from tests.ui.page_objects.home_page import HomePage
from tests.ui.page_objects.cart_page import CartPage
from tests.ui.page_objects.checkout_page import StepOnePage
from tests.ui.page_objects.checkout_page import StepTwoPage
from tests.ui.page_objects.checkout_page import FinishPage


def test_login(browser, base_url, wait):
    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)
    assert login_page.find_login_field() is not None, "Не удалось найти поле 'Логин'"
    login_page.enter_login("standard_user")
    assert login_page.find_password_field() is not None, (
        "Не удалось найти поле 'Пароль'"
    )
    login_page.enter_password("secret_sauce")
    login_page.submit_login()
    assert "/inventory.html" in browser.current_url, (
        f"Не произошел переход на страницу Products. Текущий URL: {browser.current_url}"
    )


def test_add_to_cart_from_product_page(login, browser, wait, base_url):
    browser = login
    product_page = ProductPage(browser, wait)
    product_page.open_product_page(base_url)
    assert product_page.product_image(), "Изображение товара не отображается"
    assert product_page.get_product_price(), "Отсутствует цена на товар"
    assert product_page.add_button(), "Кнопка 'Add to cart' не отображается"
    product_page.click_add_to_cart()
    assert product_page.remove_button(), "Кнопка не изменилась на 'Remove'"


def test_remove_from_cart(login, browser, wait, base_url):
    browser = login
    product_page = ProductPage(browser, wait)
    product_page.open_product_page(base_url)
    assert product_page.product_image(), "Изображение товара не отображается"
    assert product_page.get_product_price(), "Отсутствует цена на товар"
    assert product_page.add_button(), "Кнопка 'Add to cart' не отображается"
    product_page.click_add_to_cart()
    assert product_page.remove_button(), "Кнопка не изменилась на 'Remove'"
    cart_mark = CartPage(browser, wait)
    assert cart_mark.get_cart_items_count(), (
        "Счётчик не изменился, при дбавлении товара"
    )
    product_page.click_remove_from_cart()
    assert product_page.add_button(), "Кнопка не изменилась на 'Add to cart'"
    assert not cart_mark.is_cart_counter_displayed(), (
        "Счётчик корзины отображается после удаления товара"
    )


def test_going_to_the_home_page(login, browser, wait, base_url):
    browser = login
    product_page = ProductPage(browser, wait)
    product_page.open_product_page(base_url)
    product_page.back_to_products()
    assert "/inventory.html" in browser.current_url, (
        f"Не произошел переход на страницу Products. Текущий URL: {browser.current_url}"
    )


def test_add_to_cart_from_home_page(login, browser, wait, base_url):
    browser = login
    home_page = HomePage(browser, wait)
    home_page.open_home_page(base_url)
    assert home_page.product_image_hp(), "Изображение товара не отображается"
    assert home_page.get_product_price_hp(), "Отсутствует цена на товар"
    assert home_page.add_button_hp(), "Кнопка 'Add to cart' не отображается"
    home_page.click_add_to_cart_hp()
    assert home_page.remove_button_hp(), "Кнопка не изменилась на 'Remove'"
    cart_mark = CartPage(browser, wait)
    assert cart_mark.get_cart_items_count(), (
        "Счётчик не изменился, при дбавлении товара"
    )


def test_remove_from_cart_from_home_page(login, browser, wait, base_url):
    browser = login
    home_page = HomePage(browser, wait)
    home_page.open_home_page(base_url)
    assert home_page.product_image_hp(), "Изображение товара не отображается"
    assert home_page.get_product_price_hp(), "Отсутствует цена на товар"
    assert home_page.add_button_hp(), "Кнопка 'Add to cart' не отображается"
    home_page.click_add_to_cart_hp()
    assert home_page.remove_button_hp(), "Кнопка не изменилась на 'Remove'"
    cart_mark = CartPage(browser, wait)
    assert cart_mark.get_cart_items_count(), (
        "Счётчик не изменился, при дбавлении товара"
    )
    home_page.click_remove_from_cart_hp()
    assert home_page.add_button_hp(), "Кнопка не изменилась на 'Add to cart'"
    assert not cart_mark.is_cart_counter_displayed(), (
        "Счётчик корзины отображается после удаления товара"
    )


def test_changed_product_sort(login, browser, wait, base_url):
    browser = login
    home_page = HomePage(browser, wait)
    home_page.open_home_page(base_url)
    assert home_page.get_sort_value() == "az", (
        "По умолчанию должна быть выбрана сортировка 'Name (A to Z)'"
    )
    first_name_initial = home_page.get_first_product_name()
    last_name_initial = home_page.get_last_product_name()
    home_page.change_sorting("za")
    first_name_za = home_page.get_first_product_name()
    last_name_za = home_page.get_last_product_name()

    assert home_page.get_sort_value() == "za", (
        "Сортировка должна измениться на 'Name (Z to A)'"
    )
    assert first_name_za != first_name_initial, (
        "Первый товар должен измениться при смене сортировки"
    )
    assert last_name_za != last_name_initial, "Последний товар должен измениться"
    assert first_name_za == last_name_initial, (
        "Теперь первый товар должен быть последним при A-Z"
    )
    assert last_name_za == first_name_initial, (
        "Теперь последний товар должен быть первым при A-Z"
    )

    home_page.change_sorting("lohi")
    first_price_lohi = home_page.get_first_product_price()
    last_price_lohi = home_page.get_last_product_price()

    assert home_page.get_sort_value() == "lohi", (
        "Сортировка должна измениться на 'Price (low to high)'"
    )
    assert first_price_lohi <= last_price_lohi, (
        "Цены должны быть отсортированы по возрастанию"
    )

    home_page.change_sorting("hilo")
    first_price_hilo = home_page.get_first_product_price()
    last_price_hilo = home_page.get_last_product_price()

    assert home_page.get_sort_value() == "hilo", (
        "Сортировка должна измениться на 'Price (high to low)'"
    )
    assert first_price_hilo >= last_price_hilo, (
        "Цены должны быть отсортированы по убыванию"
    )


def test_purchase_product(login, browser, wait, base_url):
    browser = login
    home_page = HomePage(browser, wait)
    home_page.open_home_page(base_url)

    assert home_page.add_button_hp(), "Кнопка 'Add to cart' не отображается"
    home_page.click_add_to_cart_hp()
    assert home_page.remove_button_hp(), "Кнопка не изменилась на 'Remove'"

    cart_page = CartPage(browser, wait)
    assert cart_page.get_cart_items_count(), (
        "Счётчик не изменился при добавлении товара"
    )

    home_page.click_shopping_cart()
    assert "/cart.html" in browser.current_url, (
        f"Не произошел переход на страницу Your Cart. Текущий URL: {browser.current_url}"
    )

    cart_page.click_checkout()
    assert "/checkout-step-one.html" in browser.current_url, (
        f"Не произошел переход на страницу Checkout: Your Information. Текущий URL: {browser.current_url}"
    )

    page_one = StepOnePage(browser, wait)
    page_one.enter_first_name("Philip")
    page_one.enter_last_name("Murrey")
    page_one.enter_code("123")
    page_one.click_continue()

    assert "/checkout-step-two.html" in browser.current_url, (
        f"Не произошел переход на страницу Checkout: Overview. Текущий URL: {browser.current_url}"
    )

    page_two = StepTwoPage(browser, wait)
    page_two.click_finish_checkout()

    assert "/checkout-complete.html" in browser.current_url, (
        f"Не произошел переход на страницу Checkout: Complete!. Текущий URL: {browser.current_url}"
    )

    finish_page = FinishPage(browser, wait)
    assert finish_page.is_message_displayed(), (
        "Не найдено сообщение 'Thank you for your order!'"
    )

    finish_page.click_back_home_page()
    assert "/inventory.html" in browser.current_url, (
        f"Не вернулись на домашнюю страницу Products. Текущий URL: {browser.current_url}"
    )


def test_login_error(browser, base_url, wait):
    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)

    login_page.submit_login()

    error_text = login_page.get_error_message()
    assert error_text == "Epic sadface: Username is required", (
        f"Ожидалась ошибка 'Username is required', но получено: '{error_text}'"
    )


def test_checkout_error(login, browser, wait, base_url):
    browser = login
    home_page = HomePage(browser, wait)
    home_page.open_home_page(base_url)
    assert home_page.add_button_hp(), "Кнопка 'Add to cart' не отображается"
    home_page.click_add_to_cart_hp()
    assert home_page.remove_button_hp(), "Кнопка не изменилась на 'Remove'"
    cart_page = CartPage(browser, wait)
    assert cart_page.get_cart_items_count(), (
        "Счётчик не изменился при добавлении товара"
    )
    home_page.click_shopping_cart()
    cart_page.click_checkout()
    step_one = StepOnePage(browser, wait)
    step_one.click_continue()
    error_text = step_one.get_error_message()
    assert error_text == "Error: First Name is required", (
        f"Ожидалась ошибка 'First Name is required', но получено: '{error_text}'"
    )


# Команды для запуска:
# pytest tests/ui/test_ui.py --browser={браузер}
# pytest tests/ui/test_ui.py --browser={браузер} --alluredir=./allure-results Для фиксации
# allure serve ./allure-results - просмотр отчёта об прохождении тестов в ui формате
