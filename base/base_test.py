import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class BaseTest:
    @staticmethod
    def load_settings():
        return {
            "base_url": os.getenv(
                "UTC_LOGIN_URL", "https://vanphongdientu.utc.edu.vn/Login"
            ),
            "username": os.getenv("UTC_LOGIN_USERNAME", "huongnt"),
            "password": os.getenv("UTC_LOGIN_PASSWORD", "123456@utc"),
            "captcha_answer": os.getenv("UTC_LOGIN_CAPTCHA_ANSWER", ""),
            "timeout": float(os.getenv("UTC_LOGIN_TIMEOUT", "10")),
            "browser": os.getenv("UTC_LOGIN_BROWSER", "chrome").lower(),
            "headless": os.getenv("UTC_LOGIN_HEADLESS", "false").lower() == "true",
            "username_selector": os.getenv(
                "UTC_LOGIN_USERNAME_SELECTOR",
                "input[name='username'], input[name='email'], #username",
            ),
            "password_selector": os.getenv(
                "UTC_LOGIN_PASSWORD_SELECTOR", "input[name='userpwd'], #password"
            ),
            "submit_selector": os.getenv(
                "UTC_LOGIN_SUBMIT_SELECTOR",
                "button[type='submit'], input[type='submit']",
            ),
            "captcha_selector": os.getenv(
                "UTC_LOGIN_CAPTCHA_SELECTOR",
                "input[name='captcha'], input[name='captchaCode'], #captcha",
            ),
            "remember_selector": os.getenv(
                "UTC_LOGIN_REMEMBER_SELECTOR",
                "input[name='persistent'], input[name='remember'], #persistent",
            ),
            "error_selector": os.getenv(
                "UTC_LOGIN_ERROR_SELECTOR",
                "[role='alert'], .error, .alert-danger, .invalid-feedback",
            ),
            "success_url": os.getenv(
                "UTC_LOGIN_SUCCESS_URL_CONTAINS", "dashboard"
            ).lower(),
            "success_selector": os.getenv("UTC_LOGIN_SUCCESS_SELECTOR", ""),
            "sso_link_xpath": os.getenv(
                "UTC_LOGIN_SSO_LINK_XPATH",
                "//a[contains(normalize-space(.), 'Đăng nhập bằng e-mail UTC')]",
            ),
            "forgot_link_xpath": os.getenv(
                "UTC_LOGIN_FORGOT_LINK_XPATH",
                "//a[contains(@href, '/Login/GetPass')]",
            ),
            "sso_url": os.getenv(
                "UTC_LOGIN_SSO_URL_CONTAINS", "accounts.google.com"
            ).lower(),
            "forgot_url": os.getenv(
                "UTC_LOGIN_FORGOT_URL_CONTAINS", "getpass"
            ).lower(),
        }

    @staticmethod
    def create_driver(settings):
        if not settings["base_url"]:
            pytest.fail("Set UTC_LOGIN_URL to the UTC login page URL.")

        browser_name = settings["browser"]
        if browser_name == "chrome":
            options = ChromeOptions()
            if settings["headless"]:
                options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
        elif browser_name == "edge":
            options = EdgeOptions()
            if settings["headless"]:
                options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)
        elif browser_name == "firefox":
            options = FirefoxOptions()
            if settings["headless"]:
                options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)
        else:
            pytest.fail(
                f"Unsupported UTC_LOGIN_BROWSER '{browser_name}'. "
                "Choose chrome, edge, or firefox."
            )

        driver.set_window_size(1440, 1000)
        driver.implicitly_wait(0)
        return driver
