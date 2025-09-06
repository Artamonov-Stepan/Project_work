import allure
import pytest
from tests.db.page_objects.login_page import LoginPage
from tests.db.page_objects.main_page import MainPage


def test_creation_customer_in_db(login_as_customer, browser):
    assert "route=account/account" in browser.current_url, (
        f"Ожидался URL с 'route=account/account', текущий URL: {browser.current_url}"
    )


def test_customer_profile_data_displayed_correctly(login_as_customer, browser, wait):
    login_page = LoginPage(browser, wait)
    login_page.go_to_edit_account()

    actual_firstname = login_page.get_first_name_value()
    actual_lastname = login_page.get_last_name_value()

    assert actual_firstname == login_as_customer["firstname"], (
        f"Ожидали First Name: {login_as_customer['firstname']}, получили: {actual_firstname}"
    )
    assert actual_lastname == login_as_customer["lastname"], (
        f"Ожидали Last Name: {login_as_customer['lastname']}, получили: {actual_lastname}"
    )


def test_customer_login_with_wrong_password(
    test_customer, browser, base_url, wait, customer_data
):
    customer_id, customer_data = test_customer
    login_page = LoginPage(browser, wait)

    login_page.open_login_page(base_url)
    login_page.enter_email(customer_data["email"])
    login_page.enter_password("wrong_password123")
    login_page.submit_login()

    assert login_page.is_error_message_displayed(), (
        "Сообщение об ошибке 'No match for E-Mail Address and/or Password.' не отображается"
    )


def test_customer_deleted_from_db_cannot_login(
    db, customer_data, browser, base_url, wait
):
    customer_id = db.create_customer(customer_data)
    db.delete_customer(customer_id)

    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)
    login_page.enter_email(customer_data["email"])
    login_page.enter_password(customer_data["password"])
    login_page.submit_login()

    assert login_page.is_error_message_displayed(), (
        "Сообщение об ошибке не появилось при входе удалённого пользователя"
    )


@pytest.mark.negative
def test_delete_nonexistent_customer(db):
    with pytest.raises(ValueError, match="не найден"):
        db.delete_customer(999999)


@pytest.mark.ui
def test_user_see_test_category_in_cameras_menu(
    browser, base_url, created_test_category, test_category_data, wait
):
    main_page = MainPage(browser, wait)
    main_page.open_home_page(base_url)
    main_page.hover_and_click_cameras_menu()

    assert main_page.is_menu_item_visible(test_category_data["name"]), (
        f"Подкатегория '{test_category_data['name']}' не найдена в меню 'Cameras'"
    )


@pytest.mark.ui
def test_update_category_name_in_db(db, browser, base_url, wait):
    category_id = 33
    new_name = "Motors"
    original_name = "Cameras"
    language_id = 1

    try:
        with db.connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM oc_category_description WHERE category_id = %s AND language_id = %s",
                (category_id, language_id),
            )
            result = cursor.fetchone()
            if not result:
                pytest.fail(f"Категория {category_id} не найдена")
            original_name = result["name"]

        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE oc_category_description 
                SET name = %s 
                WHERE category_id = %s AND language_id = %s
            """,
                (new_name, category_id, language_id),
            )
            db.connection.commit()

        main_page = MainPage(browser, wait)
        main_page.open_home_page(base_url)

        main_page.click_menu_item(new_name)
        assert not main_page.is_menu_item_visible(original_name), (
            f"Старое название '{original_name}' всё ещё отображается"
        )

        # Проверка, что новое имя есть в подменю (если нужно)
        assert main_page.is_menu_item_visible(new_name), (
            f"Категория '{new_name}' не отображается в подменю"
        )
        assert not main_page.is_menu_item_visible(original_name), (
            f"Старое название '{original_name}' отображается в подменю"
        )

    except Exception as e:
        allure.attach(browser.current_url, "Current URL", allure.attachment_type.TEXT)
        allure.attach(browser.page_source, "Page Source", allure.attachment_type.HTML)
        pytest.fail(f"Ошибка при обновлении категории: {e}")
    finally:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE oc_category_description 
                SET name = %s 
                WHERE category_id = %s AND language_id = %s
            """,
                (original_name, category_id, language_id),
            )
            db.connection.commit()
        allure.attach(f"Восстановлено: '{original_name}'", name="Очистка")
