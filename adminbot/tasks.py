from adminbot.bot import bot_driver, HubBot, Hub20Bot

def www_login_read_first_mail_respond(name, username, password, receiver_id, subject, content):
    with bot_driver() as driver:
        bot = HubBot(driver, name)
        # login
        bot.log_in(username, password)
        # read first mail
        bot.read_mail()
        # respond
        bot.compose_mail(receiver_id, subject, content)

def test_login_send_private_message(name, email, inbox_path, room_id, message):
    with bot_driver() as driver:
        bot = Hub20Bot(driver, name)
        # login
        bot.log_in(inbox_path, email)
        # send private message
        bot.send_private_message(room_id, message)
