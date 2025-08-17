import pytest
import requests
from conftest import BASE_URL


def test_ping_api():
    response = requests.get(f"{BASE_URL}/ping")
    assert response.status_code == 201, (
        f"Ожидался статус 201 Created, получен {response.status_code}"
    )
    assert response.reason == "Created", (
        f"Ожидался статус 'Created', получен '{response.reason}'"
    )
    assert response.text == "Created", (
        f"Ожидалось тело ответа 'Created', получено '{response.text}'"
    )


@pytest.mark.parametrize(
    "username, password, expected_key",
    [
        ("admin", "password123", "token"),
        ("wrong_user", "wrong_pass", "reason"),
    ],
    ids=["valid_credentials", "invalid_credentials"],
)
def test_auth_api(http_session, username, password, expected_key):
    response = http_session.post(
        f"{BASE_URL}/auth",
        json={"username": username, "password": password},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200, (
        f"Ожидался статус 200, получен {response.status_code}"
    )
    data = response.json()
    assert expected_key in data, f"Ожидался ключ '{expected_key}' в ответе, но его нет"

    if expected_key == "token":
        assert data["token"], "Токен не должен быть пустым"
    else:
        assert data["reason"] == "Bad credentials", (
            f"Ожидался 'Bad credentials', получен '{data['reason']}'"
        )


def test_get_multi_bookings(booking_ids, booking_validator, http_session):
    assert len(booking_ids) >= 3, (
        f"Ожидалось не менее 3 бронирований, получено {len(booking_ids)}"
    )
    for booking_id in booking_ids:
        response = http_session.get(f"{BASE_URL}/booking/{booking_id}")
        assert response.status_code == 200, (
            f"Бронирование {booking_id} не найдено, статус: {response.status_code}"
        )
        booking_validator(response.json())


@pytest.mark.parametrize(
    "firstname, lastname, totalprice, depositpaid, checkin, checkout, additionalneeds",
    [
        ("Ivan", "Ivanov", 500, True, "2024-01-01", "2024-01-10", "Breakfast"),
        ("Anna", "Petrova", 250, False, "2024-02-01", "2024-02-15", None),
        ("Petr", "Petrov", 0, True, "2024-03-01", "2024-03-05", "Dinner"),
    ],
    ids=["with_additional", "without_additional", "minimal_price"],
)
def test_create_booking(
    firstname,
    lastname,
    totalprice,
    depositpaid,
    checkin,
    checkout,
    additionalneeds,
    create_booking,
    booking_validator,
):
    booking_data = {
        "firstname": firstname,
        "lastname": lastname,
        "totalprice": totalprice,
        "depositpaid": depositpaid,
        "bookingdates": {"checkin": checkin, "checkout": checkout},
    }
    if additionalneeds is not None:
        booking_data["additionalneeds"] = additionalneeds

    booking_id = create_booking(booking_data)

    response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert response.status_code == 200, (
        f"Ожидался статус 200, получен {response.status_code}"
    )
    created = response.json()
    booking_validator(created)

    assert created["firstname"] == firstname, (
        f"Ожидалось firstname='{firstname}', получено '{created['firstname']}'"
    )
    assert created["lastname"] == lastname, (
        f"Ожидалось lastname='{lastname}', получено '{created['lastname']}'"
    )
    assert created["totalprice"] == totalprice, (
        f"Ожидалось totalprice={totalprice}, получено {created['totalprice']}"
    )
    assert created["depositpaid"] == depositpaid, (
        f"Ожидалось depositpaid={depositpaid}, получено {created['depositpaid']}"
    )
    assert created["bookingdates"]["checkin"] == checkin, (
        f"Ожидалось checkin='{checkin}', получено '{created['bookingdates']['checkin']}'"
    )
    assert created["bookingdates"]["checkout"] == checkout, (
        f"Ожидалось checkout='{checkout}', получено '{created['bookingdates']['checkout']}'"
    )

    if additionalneeds is not None:
        assert created["additionalneeds"] == additionalneeds, (
            f"Ожидалось additionalneeds='{additionalneeds}', получено '{created['additionalneeds']}'"
        )
    else:
        assert "additionalneeds" not in created or created["additionalneeds"] is None, (
            f"Поле additionalneeds должно отсутствовать или быть None, получено: {created.get('additionalneeds')}"
        )


def test_delete_booking(create_booking, auth_token, http_session, booking_validator):
    test_data = {
        "firstname": "TestUser",
        "lastname": "DeleteMe",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"},
        "additionalneeds": "Testing",
    }

    booking_id = create_booking(test_data)

    response = http_session.get(f"{BASE_URL}/booking/{booking_id}")
    assert response.status_code == 200
    booking_validator(response.json())

    delete_response = http_session.delete(
        f"{BASE_URL}/booking/{booking_id}", headers={"Cookie": f"token={auth_token}"}
    )
    assert delete_response.status_code == 201, (
        f"Ожидался 201, получен {delete_response.status_code}"
    )

    verify_response = http_session.get(f"{BASE_URL}/booking/{booking_id}")
    assert verify_response.status_code == 404, "Бронирование не удалено"


@pytest.mark.parametrize(
    "initial_data, update_data, expected_data, unchanged_fields",
    [
        (
            {
                "firstname": "John",
                "lastname": "Doe",
                "totalprice": 100,
                "depositpaid": True,
                "bookingdates": {"checkin": "2024-01-01", "checkout": "2024-01-05"},
            },
            {"firstname": "James", "lastname": "Brown"},
            {"firstname": "James", "lastname": "Brown"},
            ["totalprice", "depositpaid", "bookingdates"],
        ),
        (
            {
                "firstname": "Alice",
                "lastname": "Smith",
                "totalprice": 200,
                "depositpaid": False,
                "bookingdates": {"checkin": "2024-02-01", "checkout": "2024-02-05"},
            },
            {"bookingdates": {"checkin": "2024-02-10", "checkout": "2024-02-15"}},
            {"bookingdates": {"checkin": "2024-02-10", "checkout": "2024-02-15"}},
            ["firstname", "lastname", "totalprice", "depositpaid"],
        ),
        (
            {
                "firstname": "Bob",
                "lastname": "Johnson",
                "totalprice": 150,
                "depositpaid": True,
                "bookingdates": {"checkin": "2024-03-01", "checkout": "2024-03-05"},
            },
            {"totalprice": 300, "depositpaid": False},
            {"totalprice": 300, "depositpaid": False},
            ["firstname", "lastname", "bookingdates"],
        ),
    ],
    ids=["update_names", "update_dates", "update_price_and_deposit"],
)
def test_partial_update_bookings(
    initial_data,
    update_data,
    expected_data,
    unchanged_fields,
    create_booking,
    auth_token,
    http_session,
    booking_validator,
):
    booking_id = create_booking(initial_data)

    update_response = http_session.patch(
        f"{BASE_URL}/booking/{booking_id}",
        json=update_data,
        headers={"Content-Type": "application/json", "Cookie": f"token={auth_token}"},
    )
    assert update_response.status_code == 200

    get_response = http_session.get(f"{BASE_URL}/booking/{booking_id}")
    assert get_response.status_code == 200
    updated = get_response.json()
    booking_validator(updated)

    for field, value in expected_data.items():
        if isinstance(value, dict):
            for k, v in value.items():
                assert updated[field][k] == v, (
                    f"Ожидалось {field}.{k}='{v}', получено '{updated[field][k]}'"
                )
        else:
            assert updated[field] == value, (
                f"Ожидалось {field}='{value}', получено '{updated[field]}'"
            )

    for field in unchanged_fields:
        assert updated[field] == initial_data[field], (
            f"Поле {field} не должно было измениться. "
            f"Ожидалось '{initial_data[field]}', получено '{updated[field]}'"
        )
