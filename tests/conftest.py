import pytest

from base.base_test import BaseTest


@pytest.fixture(scope="session")
def settings():
    return BaseTest.load_settings()


@pytest.fixture
def driver(settings):
    browser = BaseTest.create_driver(settings)
    try:
        yield browser
    finally:
        browser.quit()
