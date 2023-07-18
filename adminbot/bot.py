from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import glob
import os.path
import re

def bot_driver():
    # setup Firefox webdriver options
    options = FirefoxOptions()
    options.add_argument('-headless')
    options.log.level = 'trace'
    options.set_preference('devtools.console.stdout.content', True)
    # inizialize Firefox webdriver
    log_path = '/tmp/rq-geckodriver.log'
    service = FirefoxService(log_path=log_path, service_args=['--log', 'trace'])
    # monkey patch to fix broken logging
    service.log_file = open(log_path, "a+", encoding="utf-8")
    # next release of selenium affect this patch
    # https://github.com/SeleniumHQ/selenium/commit/ab6e4f894d58bc3a0f82577e18a7e5f7d3388ccb
    driver = webdriver.Firefox(options=options, service=service)
    driver.maximize_window()
    driver.implicitly_wait(5) # removes the need for sleep calls
    return driver


class BaseBot(object):

    def __init__(self, driver, name):
        self.driver = driver
        self.name = name

    def debug(self, s):
        print(f"[{self.__class__.__name__}] [{self.name}] [{self.driver.current_url}] {s}")


class HubBot(BaseBot):

    def __init__(self, driver, name):
        super().__init__(driver, name)

    def log_in(self, username, password):
        self.debug('Fetching the login page.')
        self.driver.get('http://www.pwnedhub.com/login')

        self.debug('Setting the inputs.')
        username_input = self.driver.find_element('name', 'username')
        password_input = self.driver.find_element('name', 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)

        self.debug('Logging in.')
        login_button = self.driver.find_element('xpath', '//input[@type="submit"]')
        login_button.click()

    def read_mail(self, count=1):
        self.debug('Visiting the inbox.')
        self.driver.get('http://www.pwnedhub.com/mail')

        self.debug('Clicking the first mail.')
        rows = self.driver.find_elements('xpath', '//tbody/tr')
        if rows and rows[0].get_attribute('onclick'):
            for row in rows[:count]:
                # click first child td to avoid bug with clicking tr elements
                row.find_elements('xpath', '*')[0].click()

    def compose_mail(self, receiver_id, subject, content):
        self.debug('Composing a mail.')
        self.driver.get('http://www.pwnedhub.com/mail/compose')

        self.debug('Setting the inputs.')
        select_input = Select(self.driver.find_element('name', 'receiver'))
        select_input.select_by_value(str(receiver_id))
        subject_input = self.driver.find_element('name', 'subject')
        subject_input.send_keys(subject)
        content_input = self.driver.find_element('name', 'content')
        content_input.send_keys(content)

        self.debug('Sending the mail.')
        login_button = self.driver.find_element('xpath', '//i[@title="Send"]')
        login_button.click()

    def log_out(self):
        self.debug('Logging out.')
        self.driver.get('http://www.pwnedhub.com/logout')


class Hub20Bot(BaseBot):

    def __init__(self, driver, name):
        super().__init__(driver, name)

    def log_in(self, username, password, inbox_path, email):
        self.debug('Fetching the login page.')
        self.driver.get('http://test.pwnedhub.com/#/login')

        self.debug('Setting the inputs.')
        username_input = self.driver.find_element('name', 'username')
        password_input = self.driver.find_element('name', 'password')
        username_input.send_keys(username)
        password_input.send_keys(password)

        self.debug('Logging in.')
        login_button = self.driver.find_element('xpath', '//input[@type="button" and @value="Log me in please."]')
        login_button.click()

        code_input = self.driver.find_element('name', 'code')
        if code_input:

            self.debug('Fetching the MFA code.')
            email_files = glob.glob(os.path.join(inbox_path, email, '*.html'))
            latest_email = max(email_files, key=os.path.getctime)
            with open(latest_email) as fp:
                match = re.search(r'<br><br>(\d{6})<br><br>', fp.read())
                code = match.group(1)

            self.debug('Setting the inputs.')
            code_input.send_keys(code)

            self.debug('Sending the MFA token.')
            mfa_button = self.driver.find_element('xpath', '//input[@type="button" and @value="Yes, it\'s really me."]')
            mfa_button.click()

    def send_private_message(self, room_id, message):
        self.debug('Visiting the Messaging view.')
        self.driver.get('http://test.pwnedhub.com/#/messaging')

        self.debug('Joining the room.')
        room_divs = self.driver.find_elements('xpath', '//div[@class="room" and @room]')
        for room_div in room_divs:
            if room_div.get_dom_attribute('id') == str(room_id):
                room_div.click()
                break

        self.debug('Setting the inputs.')
        message_input = self.driver.find_element('xpath', '//input[@type="text"]')
        message_input.send_keys(message)

        self.debug('Sending the message.')
        message_input.send_keys(Keys.ENTER)

    def log_out(self):
        self.debug('Logging out.')
        logout_span = self.driver.find_elements('xpath', '//li/span[text()="Logout"]')
        logout_span.click()
