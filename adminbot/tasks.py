from adminbot.bot import bot_driver, HubBot

def login_and_read_first_mail(host, name, username, password, receiver_id, subject, content):
    with bot_driver() as driver:
        # login and read first mail
        admin = HubBot(driver, host, name)
        admin.log_in(
            username=username,
            password=password
        )
        admin.read_mail()
        admin.compose_mail(receiver_id, subject, content)
        admin.log_out()
