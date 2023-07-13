## importing library packages
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import Select

def bot_driver():
    # setup Firefox webdriver options
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    # inizialize Firefox webdriver
    service = FirefoxService(log_path='/tmp/geckodriver.log')
    driver = webdriver.Firefox(options=options, service=service)
    driver.maximize_window()
    driver.implicitly_wait(5) # removes the need for sleep calls
    return driver


class HubBot(object):

    def __init__(self, driver, name):
        self.driver = driver
        self.name = name

    def log_in(self, username, password):
        print(f"[BOT] {self.name} is fetching the login page.")
        self.driver.get(f"http://www.pwnedhub.com/login")

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
        self.driver.get(f"http://www.pwnedhub.com/mail")

        print(f"[BOT] {self.name} is clicking the first mail.")
        rows = self.driver.find_elements('xpath', '//tbody/tr')
        if rows and rows[0].get_attribute('onclick'):
            for row in rows[:count]:
                # click first child td to avoid bug with clicking tr elements
                row.find_elements('xpath', '*')[0].click()

    def compose_mail(self, receiver_id, subject, content):
        print(f"[BOT] {self.name} is composing a mail.")
        self.driver.get(f"http://www.pwnedhub.com/mail/compose")

        print(f"[BOT] {self.name} is setting the inputs.")
        select_input = Select(self.driver.find_element('name', 'receiver'))
        select_input.select_by_value(str(receiver_id))
        subject_input = self.driver.find_element('name', 'subject')
        subject_input.send_keys(subject)
        content_input = self.driver.find_element('name', 'content')
        content_input.send_keys(content)

        print(f"[BOT] {self.name} is sending the mail.")
        login_button = self.driver.find_element('xpath', '//i[@title="Send"]')
        login_button.click()

    def log_out(self):
        print(f"[BOT] {self.name} is logging out.")
        self.driver.get(f"http://www.pwnedhub.com/logout")


class Hub20Bot(object):

    pass
