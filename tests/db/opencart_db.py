import pymysql
import bcrypt
from typing import Dict, Optional


class OpenCartDB:
    def __init__(self, connection: pymysql.connections.Connection):
        self.connection = connection

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def customer_exists(self, customer_id: int) -> bool:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM oc_customer WHERE customer_id = %s", (customer_id,)
                )
                return cursor.fetchone() is not None
        except pymysql.Error:
            return False

    def create_customer(self, customer_data: Dict) -> int:
        required_fields = ["firstname", "lastname", "email", "password"]
        if not all(field in customer_data for field in required_fields):
            raise ValueError(f"Отсутствуют обязательные поля: {required_fields}")

        try:
            with self.connection.cursor() as cursor:
                sql = """
                INSERT INTO oc_customer (
                    customer_group_id, store_id, language_id,
                    firstname, lastname, email, telephone,
                    password, custom_field, newsletter,
                    ip, status, safe, token, code, date_added
                ) VALUES (
                    1, 0, 1, %s, %s, %s, %s,
                    %s, '', 0, '', 1, 0, '', '', NOW()
                )
                """
                hashed_password = self._hash_password(customer_data["password"])
                cursor.execute(
                    sql,
                    (
                        customer_data["firstname"],
                        customer_data["lastname"],
                        customer_data["email"],
                        customer_data.get("telephone", ""),
                        hashed_password,
                    ),
                )
                self.connection.commit()
                return cursor.lastrowid
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при создении клиента: {e}")

    def delete_customer(self, customer_id: int) -> bool:
        if not self.customer_exists(customer_id):
            raise ValueError(f"Клиент с ID {customer_id} не найден")

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM oc_customer WHERE customer_id = %s", (customer_id,)
                )
                self.connection.commit()
                return cursor.rowcount > 0
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при удалении клиента: {e}")

    def delete_category(self, category_id: int):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM oc_category WHERE category_id = %s", (category_id,)
                )
                cursor.execute(
                    "DELETE FROM oc_category_description WHERE category_id = %s",
                    (category_id,),
                )
                cursor.execute(
                    "DELETE FROM oc_seo_url WHERE `value` LIKE %s",
                    (f"%_{category_id}",),
                )
                cursor.execute(
                    "DELETE FROM oc_category_to_store WHERE category_id = %s",
                    (category_id,),
                )
            self.connection.commit()
        except pymysql.Error as e:
            self.connection.rollback()
            raise RuntimeError(f"Ошибка при удалении категории {category_id}: {e}")
