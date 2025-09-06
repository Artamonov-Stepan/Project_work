import pytest
import pymysql
import logging
import allure
import socket
from selenium.webdriver.support import expected_conditions as EC
from tests.db.page_objects.login_page import LoginPage
from .opencart_db import OpenCartDB


def pytest_addoption(parser):
    try:
        socket.gethostbyname("mariadb")
        default_host = "mariadb"
    except socket.gaierror:
        default_host = "127.0.0.1"
    parser.addoption("--host", default=default_host)
    parser.addoption("--port", type=int, default=3306)
    parser.addoption("--db", default="bitnami_opencart")
    parser.addoption("--user", default="bn_opencart")
    parser.addoption("--password", default="")


@pytest.fixture(scope="session")
def base_url(request):
    return "http://192.168.0.7:8081"


@pytest.fixture(scope="session")
def db_connection(request):
    try:
        connection = pymysql.connect(
            host=request.config.getoption("--host"),
            port=request.config.getoption("--port"),
            user=request.config.getoption("--user"),
            password=request.config.getoption("--password"),
            database=request.config.getoption("--db"),
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
        )
        yield connection
        connection.close()
    except Exception as e:
        pytest.skip(f"Не удалось подключиться к БД: {e}")


@pytest.fixture(scope="session")
def db(db_connection):
    if db_connection is None:
        pytest.skip("Нет подключения к БД")
    return OpenCartDB(db_connection)


@pytest.fixture
def customer_data():
    from faker import Faker

    fake = Faker("en_US")
    return {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "email": fake.unique.email(),
        "password": fake.password(length=12),
        "telephone": fake.phone_number(),
    }


@pytest.fixture
def test_customer(db, customer_data):
    customer_id = db.create_customer(customer_data)
    yield customer_id, customer_data

    try:
        if db.customer_exists(customer_id):
            db.delete_customer(customer_id)
    except Exception as e:
        logging.warning(f"Ошибка при удалении тестового клиента {customer_id}: {e}")


@pytest.fixture
def login_as_customer(db, customer_data, browser, base_url, wait):
    customer_id = db.create_customer(customer_data)
    login_page = LoginPage(browser, wait)
    login_page.open_login_page(base_url)
    login_page.is_login_form_present()
    login_page.enter_email(customer_data["email"])
    login_page.enter_password(customer_data["password"])
    login_page.submit_login()

    wait.until(EC.url_contains("route=account/account"))
    assert f"Клиент {customer_data['email']} успешно авторизовался"

    yield customer_data

    try:
        if db.customer_exists(customer_id):
            db.delete_customer(customer_id)
    except Exception as e:
        logging.warning(f"Ошибка при удалении клиента {customer_id}: {e}")


@pytest.fixture
def test_category_data():
    return {
        "name": "Test Auto Category",
        "description": "This category is created and removed automatically by a test.",
        "meta_title": "Auto Test Category",
        "keyword": "test_categories_01",
    }


@pytest.fixture
def created_test_category(db, test_category_data):
    parent_id = 33
    parent_keyword = "cameras"
    subcategory_id = None

    try:
        with db.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO oc_category 
                (image, parent_id, top, `column`, sort_order, status, date_added, date_modified)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """,
                ("", parent_id, 1, 1, 0, 1),
            )
            subcategory_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO oc_category_description 
                (category_id, language_id, name, description, meta_title, meta_description, meta_keyword)
                VALUES (%s, 1, %s, %s, %s, %s, %s)
            """,
                (
                    subcategory_id,
                    test_category_data["name"],
                    test_category_data["description"],
                    test_category_data["meta_title"],
                    "",
                    "",
                ),
            )

            full_keyword = f"{parent_keyword}/{test_category_data['keyword']}"
            cursor.execute(
                """
                INSERT INTO oc_seo_url 
                (store_id, language_id, `key`, `value`, keyword, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (0, 1, "path", f"33_{subcategory_id}", full_keyword, 0),
            )

            cursor.execute(
                """
                INSERT INTO oc_category_to_store (category_id, store_id)
                VALUES (%s, %s)
            """,
                (subcategory_id, 0),
            )

            db.connection.commit()

        allure.attach(
            f"Создана категория: {test_category_data['name']} (ID={subcategory_id}, SEO: {full_keyword})",
            name="Создание тестовой категории",
            attachment_type=allure.attachment_type.TEXT,
        )

        yield subcategory_id

    except Exception as e:
        db.connection.rollback()
        allure.attach(
            str(e), "Ошибка при создании категории", allure.attachment_type.TEXT
        )
        pytest.fail(f"Не удалось создать тестовую категорию: {e}")
    finally:
        if subcategory_id:
            db.delete_category(subcategory_id)
            allure.attach(
                f"Категория {subcategory_id} удалена из БД",
                name="Очистка после теста",
                attachment_type=allure.attachment_type.TEXT,
            )
