ROLES = {
    0: 'admin',
    1: 'user',
}

USER_STATUSES = {
    0: 'disabled',
    1: 'enabled',
}

QUESTIONS = {
    0: 'Favorite food?',
    1: 'Pet\'s name?',
    2: 'High school mascot?',
    3: 'Birthplace?',
    4: 'First employer?',
}

DEFAULT_NOTE = '''##### Welcome to PwnedHub!

A collaborative space to conduct hosted security assessments.

**Find flaws.**

* This is your notes space. Keep your personal notes here.
* Store artifacts from local and external tools in the artifacts space.
* Leverage popular security testing tools right from your browser in the tools space.

**Collaborate.**

* Privately collaborate with coworkers in the PwnMail space.
* Share public information and socialize in the messages space.

Happy hunting!

\\- The PwnedHub Team

'''

ADMIN_RESPONSE = {
    'default': 'I would be more than happy to help you with that. Unfortunately, the person responsible for that is unavailable at the moment. We\'ll get back with you soon. Thanks.',
    'password': 'Hey no problem. We all forget our password every now and then. Your current password is {password}, but you can simply reset it using the Forgot Password link on the login page. I hope this helps. Have a great day!'
}
