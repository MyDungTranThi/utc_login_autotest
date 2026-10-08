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

def test_TC05_unknown_username_is_rejected(login_page):
    login_page.login("user_not_exist_999", "Abc@123")
    login_page.assert_login_rejected()
    assert login_page.error_message(), "Expected an authentication failure message."

def test_TC06_valid_username_wrong_password_is_rejected(login_page, settings):
    username, _ = _valid_credentials(settings, "TC06")
    login_page.login(username, "WrongPassword123")
    login_page.assert_login_rejected()
    assert login_page.error_message(), "Expected an authentication failure message."

def test_TC07_wrong_username_valid_password_is_rejected(login_page, settings):
    _, password = _valid_credentials(settings, "TC07")
    login_page.login("wrong_user", password)
    login_page.assert_login_rejected()


def _fail_login_attempts(login_page, username, count):
    for _ in range(count):
        login_page.login(username, "WrongPassword123")
        login_page.assert_login_rejected()


def test_TC08_captcha_not_shown_after_first_failure(login_page, settings):
    username, _ = _valid_credentials(settings, "TC08")
    _fail_login_attempts(login_page, username, 1)
    assert login_page.captcha_input() is None, (
        "CAPTCHA appeared before the third failed login attempt."
    )

def test_TC09_captcha_not_shown_after_second_failure(login_page, settings):
    username, _ = _valid_credentials(settings, "TC09")
    _fail_login_attempts(login_page, username, 2)
    assert login_page.captcha_input() is None, (
        "CAPTCHA appeared before the third failed login attempt."
    )

def test_TC10_captcha_shown_after_third_failure(login_page, settings):
    username, _ = _valid_credentials(settings, "TC10")
    _fail_login_attempts(login_page, username, 3)
    assert login_page.captcha_input() is not None, (
        "Expected CAPTCHA to appear after three failed login attempts."
    )

def test_TC11_valid_password_without_captcha_is_rejected(login_page, settings):
    username, password = _valid_credentials(settings, "TC11")
    _fail_login_attempts(login_page, username, 3)
    assert login_page.captcha_input() is not None, "CAPTCHA was not presented."
    login_page.login(username, password)
    login_page.assert_login_rejected()
    assert login_page.captcha_input() is not None or login_page.error_message(), (
        "Expected CAPTCHA-required validation."
    )

def test_TC12_correct_captcha_and_password_open_dashboard(login_page, settings):
    username, password = _valid_credentials(settings, "TC12")
    captcha_answer = settings["captcha_answer"]
    assert captcha_answer, (
        "Set UTC_LOGIN_CAPTCHA_ANSWER to a valid CAPTCHA answer in the test "
        "environment."
    )
    _fail_login_attempts(login_page, username, 3)
    login_page.login(username, password, captcha_answer)
    assert login_page.is_logged_in(), (
        "Valid credentials and CAPTCHA did not open the dashboard."
    )


def test_TC13_wrong_captcha_is_rejected(login_page, settings):
    username, password = _valid_credentials(settings, "TC13")
    _fail_login_attempts(login_page, username, 3)
    login_page.login(username, password, "invalid-captcha-answer")
    login_page.assert_login_rejected()
    assert login_page.error_message(), "Expected an invalid-CAPTCHA message."

@pytest.mark.parametrize(
    ("case_id", "username", "password"),
    [
        ("TC14", "  user01  ", "configured"),
        ("TC15", "configured", "  password123  "),
    ],
    ids=["TC14-username-surrounding-spaces", "TC15-password-surrounding-spaces"],
)
def test_whitespace_credentials_do_not_crash(
    login_page, settings, case_id, username, password
):
    valid_username = _username(settings, case_id)
    password_value = settings["password"] if password == "configured" else password
    assert password_value, "Set UTC_LOGIN_PASSWORD to a test account password."
    login_page.login(
        valid_username if username == "configured" else username,
        password_value,
    )
    login_page.assert_no_server_error(case_id)

def test_TC16_special_characters_are_rejected_safely(login_page):
    login_page.login("!@#$%^&*()", "Abc@123")
    login_page.assert_login_rejected()
    assert not login_page.has_sql_error(), "SQL/database error was exposed."

def test_TC17_oversized_username_does_not_crash_or_authenticate(login_page):
    login_page.login("u" * 500, "Abc@123")
    login_page.assert_login_rejected()
    login_page.assert_no_server_error("Oversized username")
    assert not login_page.has_sql_error(), "SQL/database error was exposed."

def test_TC18_oversized_password_does_not_crash_or_authenticate(
    login_page, settings
):
    username, _ = _valid_credentials(settings, "TC18")
    login_page.login(username, "p" * 500)
    login_page.assert_login_rejected()
    login_page.assert_no_server_error("Oversized password")

@pytest.mark.parametrize(
    ("case_id", "username", "password"),
    [
        ("TC19", "' OR '1'='1", "anything"),
        ("TC20", "configured", "' OR '1'='1"),
        ("TC21", "admin' --", "anything"),
    ],
    ids=[
        "TC19-sql-injection-username",
        "TC20-sql-injection-password",
        "TC21-sql-comment-injection",
    ],
)
def test_sql_injection_payloads_do_not_bypass_authentication(
    login_page, settings, case_id, username, password
):
    username_value = (
        _username(settings, case_id) if username == "configured" else username
    )
    assert username_value, (
        f"Set UTC_LOGIN_USERNAME or UTC_LOGIN_USERNAME_{case_id} "
        "to the valid test account username."
    )
    login_page.login(username_value, password)
    login_page.assert_login_rejected()
    assert not login_page.has_sql_error(), "SQL/database error was exposed."

def test_TC22_password_input_is_masked(login_page):
    assert login_page.password_input().get_attribute("type") == "password"
