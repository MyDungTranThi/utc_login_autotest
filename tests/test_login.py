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

