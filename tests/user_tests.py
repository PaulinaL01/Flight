import unittest
from selenium.webdriver import Chrome
from page_objects import SignUpPage
from parameterized import parameterized

DRIVER_PATH = r"C:\Users\lesni\OneDrive\Pulpit\chromedriver.exe"
WEBSITE_URL = r"http://127.0.0.1:5000/"


class UserTestCases(unittest.TestCase):
    def setUp(self):
        self.driver = Chrome(DRIVER_PATH)
        self.driver.get(WEBSITE_URL)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        self.driver.close()

    @parameterized.expand([
        ("123456A", "123456A", "Field must be between 8 and 30 characters long."),
        ("11111111111111111111111111A", "11111111111111111111111111A", "Field must be between 8 and 30 characters long.")
    ])
    def test_create_user_invalid_password_0(self, password1_value, password2_value, expected_message):
        login_value = "test22"
        email_value = "test22@test.pl"

        signup_element = self.driver.find_element_by_css_selector("a[href='/signup']")
        signup_element.click()

        # login_field = self.driver.find_element_by_id("login")
        # login_field.send_keys(login_value)
        #
        # email_field = self.driver.find_element_by_id("email")
        # email_field.send_keys(email_value)
        #
        # password1_field = self.driver.find_element_by_id("password1")
        # password1_field.send_keys(password1_value)
        #
        # password2_field = self.driver.find_element_by_id("password2")
        # password2_field.send_keys(password2_value)
        #
        # button_submit = self.driver.find_element_by_css_selector("button[type='submit']")
        # button_submit.click()
        #
        # alert = self.driver.find_element_by_name("alert")
        # self.assertEqual(expected_message, alert.text)

        alert_message = SignUpPage(self.driver)\
                        .set_login(login_value)\
                        .set_email(email_value)\
                        .set_password1(password1_value)\
                        .set_password2(password2_value)\
                        .click_submit()\
                        .get_first_alert_message()
        self.assertEqual(alert_message, expected_message)


if __name__ == '__main__':
    unittest.main()
