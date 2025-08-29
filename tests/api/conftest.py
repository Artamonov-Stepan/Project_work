from typing import Dict, List, Union, Optional
import pytest
import requests
import allure

BASE_URL = "https://restful-booker.herokuapp.com"


BookingType = Dict[str, Union[str, int, float, bool, Dict[str, str], Optional[str]]]


@pytest.fixture(scope="session")
def http_session():
    with requests.Session() as session:
        yield session


@pytest.fixture(scope="module")
def booking_ids(http_session) -> List[int]:
    with allure.step("Получаю список ID бронирований"):
        response = http_session.get(f"{BASE_URL}/booking")
        response.raise_for_status()
        ids = [item["bookingid"] for item in response.json()][:3]
        allure.attach(
            "\n".join(map(str, ids)),
            name="Список booking IDs",
            attachment_type=allure.attachment_type.TEXT,
        )
        return ids


@allure.step("Проверяю структуру бронирования")
def booking_validator(booking: BookingType):
    REQUIRED_FIELDS = {
        "firstname": str,
        "lastname": str,
        "totalprice": (int, float),
        "depositpaid": bool,
        "bookingdates": dict,
    }

    for field, expected_type in REQUIRED_FIELDS.items():
        assert field in booking, f"Отсутствует обязательное поле: {field}"
        assert isinstance(booking[field], expected_type), (
            f"Поле '{field}' имеет неверный тип. "
            f"Ожидается: {expected_type}, получено: {type(booking[field])}"
        )

    dates = booking["bookingdates"]
    assert all(k in dates for k in ["checkin", "checkout"]), (
        "Отсутствуют даты бронирования"
    )
    assert all(
        isinstance(dates[k], str) and len(dates[k]) == 10
        for k in ["checkin", "checkout"]
    ), "Неверный формат даты"

    if "additionalneeds" in booking:
        assert isinstance(booking["additionalneeds"], (str, type(None))), (
            "Поле 'additionalneeds' должно быть строкой или None"
        )


@pytest.fixture
def auth_token(http_session):
    with allure.step("Получаю токен авторизации"):
        auth_data = {"username": "admin", "password": "password123"}
        try:
            response = http_session.post(f"{BASE_URL}/auth", json=auth_data)
            response.raise_for_status()
            token = response.json()["token"]
            allure.attach(token, "Auth Token", allure.attachment_type.TEXT)
            return token
        except Exception as e:
            pytest.fail(f"Не удалось получить токен: {e}")


@pytest.fixture
def create_booking(http_session, auth_token):
    created_bookings = []

    @allure.step("Создаю новое бронирование")
    def _create(booking_data):
        response = http_session.post(
            f"{BASE_URL}/booking",
            json=booking_data,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200, (
            f"Ошибка создания бронирования: {response.text}"
        )
        booking_id = response.json()["bookingid"]
        created_bookings.append(booking_id)
        allure.attach(
            f"Создано бронирование с ID: {booking_id}",
            "ID бронирования",
            allure.attachment_type.TEXT,
        )
        return booking_id

    yield _create

    with allure.step("Удаляю созданные бронирования"):
        for booking_id in created_bookings:
            response = http_session.delete(
                f"{BASE_URL}/booking/{booking_id}",
                headers={"Cookie": f"token={auth_token}"},
            )
            if response.status_code == 201:
                allure.attach(f"Бронирование {booking_id} удалено", "Cleanup")
            else:
                allure.attach(
                    f"Ошибка при удалении {booking_id}: {response.status_code}",
                    "Cleanup Warning",
                    allure.attachment_type.TEXT,
                )
