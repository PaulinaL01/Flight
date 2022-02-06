class SignUpPage:
    def __init__(self, driver):
        self.driver = driver

    def set_login(self, login):
        field = self.driver.find_element_by_id("login")
        field.send_keys(login)
        return self

    def set_email(self, email):
        field = self.driver.find_element_by_id("email")
        field.send_keys(email)
        return self

    def set_password1(self, password1):
        field = self.driver.find_element_by_id("password1")
        field.send_keys(password1)
        return self

    def set_password2(self, password2):
        field = self.driver.find_element_by_id("password2")
        field.send_keys(password2)
        return self

    def click_submit(self):
        button_submit = self.driver.find_element_by_css_selector("button[type='submit']")
        button_submit.click()
        return self

    def get_first_alert_message(self):
        return self.driver.find_element_by_name("alert").text
