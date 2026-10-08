# UTC login Selenium tests

This project contains Selenium WebDriver tests based on
`Test_Case_Trang_Dang_Nhap_UTC.xlsx`. It uses Python, pytest, and Selenium 4.
The suite includes all 25 test cases from the workbook. Some cases require
valid account credentials and repeated failed logins; configure a dedicated
test account before running those cases. Repeated failures can trigger CAPTCHA
or account lockout on the live site, so a test environment is strongly
recommended.

## Project structure

```text
base/
  base_test.py       # WebDriver setup and test configuration
pages/
  base_page.py       # Shared page actions and waits
  login_page.py      # Login page objects and actions
tests/
  conftest.py        # Pytest fixtures
  test_login.py      # Login test scripts
```

## Install and run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure test credentials and run the suite from the project directory:

```powershell
$env:UTC_LOGIN_USERNAME = "test-user"
$env:UTC_LOGIN_PASSWORD = "test-password"
python -m pytest
```

`UTC_LOGIN_URL` defaults to `https://vanphongdientu.utc.edu.vn/Login`.

Selenium Manager obtains the browser driver automatically. Chrome runs headless
by default. Set `UTC_LOGIN_HEADLESS=false` to show the browser, or set
`UTC_LOGIN_BROWSER` to `edge` or `firefox`.

## Application-specific configuration

The workbook does not specify a URL, HTML locators, or route names. The suite
uses conventional defaults; override them for the target test environment:

| Variable | Default / purpose |
| --- | --- |
| `UTC_LOGIN_USERNAME_SELECTOR` | `input[name='username'], input[name='email'], #username` |
| `UTC_LOGIN_PASSWORD_SELECTOR` | `input[name='userpwd'], #password` |
| `UTC_LOGIN_SUBMIT_SELECTOR` | `button[type='submit'], input[type='submit']` |
| `UTC_LOGIN_CAPTCHA_SELECTOR` | `input[name='captcha'], input[name='captchaCode'], #captcha` |
| `UTC_LOGIN_CAPTCHA_ANSWER` | Valid CAPTCHA answer in the test environment (TC12) |
| `UTC_LOGIN_REMEMBER_SELECTOR` | `input[name='persistent'], input[name='remember'], #persistent` |
| `UTC_LOGIN_ERROR_SELECTOR` | Common alert/error elements |
| `UTC_LOGIN_SUCCESS_URL_CONTAINS` | `dashboard`; set `UTC_LOGIN_SUCCESS_SELECTOR` as an alternative |
| `UTC_LOGIN_SUCCESS_SELECTOR` | Optional CSS selector that is visible after login |
| `UTC_LOGIN_SSO_LINK_XPATH` | Link text containing “Đăng nhập bằng e-mail UTC” |
| `UTC_LOGIN_SSO_URL_CONTAINS` | `accounts.google.com` |
| `UTC_LOGIN_FORGOT_LINK_XPATH` | `//a[contains(@href, '/Login/GetPass')]` |
| `UTC_LOGIN_FORGOT_URL_CONTAINS` | `getpass` (`/Login/GetPass`) |
| `UTC_LOGIN_TIMEOUT` | Explicit Selenium wait timeout in seconds (`10`) |

Set `UTC_LOGIN_USERNAME_TC06`, `UTC_LOGIN_USERNAME_TC08`, etc. to use a
separate account for a particular case; otherwise each case uses
`UTC_LOGIN_USERNAME`. This is important for TC08–TC13: failed-login counts are
maintained by the server and can affect later tests. Use separate test accounts
or reset the failed-login counter between CAPTCHA cases.

The Remember Me checkbox is visually hidden on the live page, so TC23 clicks
its associated visible label. TC23 then requires valid test credentials and
checks that the password is not stored as plaintext in browser storage or
cookies.
