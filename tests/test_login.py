import os

import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage


def _username(settings, case_id):
    return os.getenv(f"UTC_LOGIN_USERNAME_{case_id}", settings["username"])


def _valid_credentials(settings, case_id):
    username = _username(settings, case_id)
    password = settings["password"]
    assert username, (
        f"Set UTC_LOGIN_USERNAME or UTC_LOGIN_USERNAME_{case_id} "
        "to the valid test account username."
    )
    assert password, "Set UTC_LOGIN_PASSWORD to the valid test account password."
    return username, password


@pytest.fixture
def login_page(driver, settings):
    page = LoginPage(driver, settings)
    page.open()
    return page


def test_TC01_valid_credentials_open_dashboard(login_page, settings):
    username, password = _valid_credentials(settings, "TC01")
    login_page.login(username, password)
    assert login_page.is_logged_in(), ("Valid credentials did not open the dashboard.")

@pytest.mark.parametrize(
    ("case_id", "username", "password"),
    [
        ("TC02", "", "not-used-test-password"),
        ("TC03", "not-used-test-user", ""),
        ("TC04", "", ""),
    ],
    ids=["TC02-empty-username", "TC03-empty-password", "TC04-both-empty"],
)
def test_required_login_fields(login_page, case_id, username, password):
    login_page.fill(username=username, password=password)
    username_input = login_page.username_input()
    password_input = login_page.password_input()
    username_invalid = login_page.field_is_required(username_input)
    password_invalid = login_page.field_is_required(password_input)
    login_page.submit()

    assert username_invalid or login_page.error_message(), (
        f"{case_id}: expected required-field validation."
    )
    assert password_invalid or login_page.error_message(), (
        f"{case_id}: expected required-field validation."
    )
    assert login_page.driver.current_url.rstrip("/").lower().endswith("/login"), (
        f"{case_id}: blank credentials unexpectedly navigated away from login."
    )


