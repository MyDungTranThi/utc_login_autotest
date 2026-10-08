import logging
import re

import allure
import pytest
from selenium.common.exceptions import WebDriverException

from base.base_test import BaseTest

LOGGER = logging.getLogger(__name__)


CASE_TITLES = {
    "TC01": "Valid credentials open dashboard",
    "TC02": "Username is empty",
    "TC03": "Password is empty",
    "TC04": "Username and password are empty",
    "TC05": "Unknown username is rejected",
    "TC06": "Valid username with incorrect password is rejected",
    "TC07": "Incorrect username with valid password is rejected",
    "TC08": "CAPTCHA is absent after first failed login",
    "TC09": "CAPTCHA is absent after second failed login",
    "TC10": "CAPTCHA appears after third failed login",
    "TC11": "Login without required CAPTCHA is rejected",
    "TC12": "Valid CAPTCHA and password open dashboard",
    "TC13": "Incorrect CAPTCHA is rejected",
    "TC14": "Username with surrounding whitespace",
    "TC15": "Password with surrounding whitespace",
    "TC16": "Special characters in username are handled safely",
    "TC17": "Oversized username is handled safely",
    "TC18": "Oversized password is handled safely",
    "TC19": "SQL injection in username does not bypass authentication",
    "TC20": "SQL injection in password does not bypass authentication",
    "TC21": "SQL comment injection does not bypass authentication",
    "TC22": "Password is masked",
    "TC23": "Remember Me checkbox works",
    "TC24": "UTC email login redirects to SSO",
    "TC25": "Forgot Password link opens its page",
}


@pytest.fixture(scope="session")
def settings():
    return BaseTest.load_settings()


@pytest.fixture(autouse=True)
def allure_test_metadata(request):
    case_match = re.search(r"TC\d{2}", request.node.nodeid)
    if case_match:
        case_id = case_match.group()
        allure.dynamic.feature("UTC Login")
        allure.dynamic.story(f"{case_id}: {CASE_TITLES[case_id]}")
        allure.dynamic.title(f"{case_id} - {CASE_TITLES[case_id]}")


@pytest.fixture
def driver(settings):
    browser = BaseTest.create_driver(settings)
    try:
        yield browser
    finally:
        browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return

    browser = item.funcargs.get("driver")
    if browser is None:
        return

    try:
        allure.attach(
            browser.get_screenshot_as_png(),
            name="Failure screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    except WebDriverException as error:
        LOGGER.warning("Could not attach failure screenshot: %s", error)
