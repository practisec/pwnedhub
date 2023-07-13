from adminbot.bot import bot_driver, HubBot

def login_read_first_mail_respond(name, username, password, receiver_id, subject, content):
    with bot_driver() as driver:
        # login
        admin = HubBot(driver, name)
        admin.log_in(
            username=username,
            password=password
        )
        # read first mail
        admin.read_mail()
        # respond
        admin.compose_mail(receiver_id, subject, content)
