## importing library packages
from selenium import webdriver

def bot_driver():
    # setup Firefox webdriver options
    options=webdriver.FirefoxOptions()
    options.headless = True
    # inizialize Firefox webdriver
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.implicitly_wait(5) # removes the need for sleep calls
    return driver


class BaseBot(object):

    def __init__(self, driver, host, name):
        self.driver = driver
        self.host = host
        self.name = name

    def log_in(self, username, password):
        print(f"[BOT] {self.name} is fetching the login page.")
        self.driver.get(f"http://{self.host}/login")

        print(f"[BOT] {self.name} is setting the inputs.")
        username_input = self.driver.find_element('name', 'username')
        password_input = self.driver.find_element('name', 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)

        print(f"[BOT] {self.name} is logging in.")
        login_button = self.driver.find_element('xpath', '//input[@type="submit"]')
        login_button.click()

    def read_mail(self, count=1):
        print(f"[BOT] {self.name} is visiting their inbox.")
        self.driver.get(f"http://{self.host}/mail")

        print(f"[BOT] {self.name} is clicking the first mail.")
        rows = self.driver.find_elements('xpath', '//tbody/tr')
        if rows and rows[0].get_attribute('onclick'):
            for row in rows[:count]:
                # click first child td to avoid bug with clicking tr elements
                row.find_elements('xpath', '*')[0].click()

    def log_out(self):
        print(f"[BOT] {self.name} is logging out.")
        self.driver.get(f"http://{self.host}/logout")


class AdminBot(BaseBot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
