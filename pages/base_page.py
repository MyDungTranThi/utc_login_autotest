from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings["timeout"])

    def visible(self, by, selector):
        elements = self.driver.find_elements(by, selector)
        return next((element for element in elements if element.is_displayed()), None)

    def required_visible(self, by, selector, description):
        return self.wait.until(
            lambda _driver: self.visible(by, selector),
            message=f"Could not find visible {description}: {selector}",
        )

    def required_present(self, by, selector, description):
        return self.wait.until(
            EC.presence_of_element_located((by, selector)),
            message=f"Could not find {description}: {selector}",
        )

    def click_link(self, xpath, expected_url_contains):
        link = self.required_present(By.XPATH, xpath, "link")
        self.driver.execute_script("arguments[0].click();", link)
        self.wait.until(
            lambda driver: expected_url_contains in driver.current_url.lower(),
            message=(
                "Clicking the link did not navigate to a URL containing "
                f"'{expected_url_contains}'. Current URL: {self.driver.current_url}"
            ),
        )
