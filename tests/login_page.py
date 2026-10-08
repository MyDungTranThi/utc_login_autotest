from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings["timeout"])

    def open(self):
        self.driver.get(self.settings["base_url"])
        self.username_input()

    def _visible(self, by, selector):
        elements = self.driver.find_elements(by, selector)
        return next((element for element in elements if element.is_displayed()), None)

    def _required_visible(self, by, selector, description):
        return self.wait.until(
            lambda _driver: self._visible(by, selector),
            message=f"Could not find visible {description}: {selector}",
        )

    def _required_present(self, by, selector, description):
        return self.wait.until(
            EC.presence_of_element_located((by, selector)),
            message=f"Could not find {description}: {selector}",
        )

    def username_input(self):
        return self._required_visible(
            By.CSS_SELECTOR, self.settings["username_selector"], "username input"
        )

    def password_input(self):
        return self._required_visible(
            By.CSS_SELECTOR, self.settings["password_selector"], "password input"
        )

    def captcha_input(self):
        return self._visible(By.CSS_SELECTOR, self.settings["captcha_selector"])

    def error_message(self):
        return self._visible(By.CSS_SELECTOR, self.settings["error_selector"])

    @staticmethod
    def _set_value(field, value):
        field.clear()
        if value:
            field.send_keys(value)

    def fill(self, username=None, password=None, captcha=None):
        if username is not None:
            self._set_value(self.username_input(), username)
        if password is not None:
            self._set_value(self.password_input(), password)
        if captcha is not None:
            field = self._required_visible(
                By.CSS_SELECTOR, self.settings["captcha_selector"], "CAPTCHA input"
            )
            self._set_value(field, captcha)

    def submit(self):
        button = self._required_visible(
            By.CSS_SELECTOR, self.settings["submit_selector"], "login submit button"
        )
        button.click()

    def login(self, username, password, captcha=None):
        self.fill(username=username, password=password, captcha=captcha)
        self.submit()

    def click_link(self, xpath, expected_url_contains):
        link = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.execute_script("arguments[0].click();", link)
        self.wait.until(
            lambda driver: expected_url_contains in driver.current_url.lower(),
            message=(
                "Clicking the link did not navigate to a URL containing "
                f"'{expected_url_contains}'. Current URL: {self.driver.current_url}"
            ),
        )

    def is_logged_in(self):
        success_selector = self.settings["success_selector"]
        if success_selector:
            return self.wait.until(
                lambda _driver: self._visible(By.CSS_SELECTOR, success_selector)
            ) is not None
        success_url = self.settings["success_url"]
        if not success_url:
            raise AssertionError(
                "Set UTC_LOGIN_SUCCESS_SELECTOR or UTC_LOGIN_SUCCESS_URL_CONTAINS "
                "to define a successful login."
            )
        return self.wait.until(
            lambda driver: success_url in driver.current_url.lower()
        )

    def assert_login_rejected(self):
        success_url = self.settings["success_url"]
        if success_url:
            assert success_url not in self.driver.current_url.lower(), (
                f"Unexpectedly reached authenticated URL: {self.driver.current_url}"
            )
        assert self._visible(
            By.CSS_SELECTOR, self.settings["username_selector"]
        ) is not None, "Login form disappeared after an unsuccessful login."

    def has_sql_error(self):
        text = self.driver.page_source.lower()
        indicators = (
            "sql syntax",
            "sqlstate",
            "syntax error",
            "sql exception",
            "mysql",
            "postgresql",
            "ora-",
            "odbc",
            "database error",
        )
        return any(indicator in text for indicator in indicators)

    @staticmethod
    def field_is_required(field):
        try:
            return field.get_property("required") or not field.get_property(
                "validity"
            )["valid"]
        except (NoSuchElementException, TypeError):
            return False
