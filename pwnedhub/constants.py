ROLES = {
    0: 'admin',
    1: 'user',
}

USER_STATUSES = {
    0: 'disabled',
    1: 'enabled',
}

BUG_STATUSES = {
    0: 'submitted',
    # anything below is considered validated
    1: 'rejected',
    2: 'confirmed',
    3: 'fixed',
}

VULNERABILITIES = {
    0: ('Server Security Misconfiguration', 100),
    1: ('Server-Side Injection', 500),
    2: ('Broken Authentication and Session Management', 300),
    3: ('Sensitive Data Exposure', 100),
    4: ('Cross-Site Scripting (XSS)', 200),
    5: ('Broken Access Control (BAC)', 400),
    6: ('Cross-Site Request Forgery (CSRF)', 200),
    7: ('Application-Level Denial-of-Service (DoS)', 100),
    8: ('Unvalidated Redirects and Forwards', 100),
    9: ('External Behavior', 100),
    10: ('Insufficient Security Configurability', 100),
    11: ('Using Components with Known Vulnerabilities', 200),
    12: ('Insecure Data Storage', 100),
    13: ('Insecure Data Transport', 300),
    14: ('Broken Cryptography', 100),
    15: ('Privacy Concerns', 100),
    16: ('Other', 100),
}

SEVERITY = {
    0: 'informational',
    1: 'low',
    2: 'medium',
    3: 'high',
    4: 'critical',
}

QUESTIONS = {
    0: 'Favorite food?',
    1: 'Pet\'s name?',
    2: 'High school mascot?',
    3: 'Birthplace?',
    4: 'First employer?',
}

DEFAULT_NOTE = '''Welcome to PwnedHub! A collaborative space to conduct security assessments.

* This is your notes space. Keep your personal notes here.

* Store artifacts from local and external tools in the artifacts space.

* Leverage popular security testing tools right from your browser in the tools space.

* Privately collaborate with coworkers in the mailbox space.

* Share information and socialize in the messages space.

Happy testing!

- The PwnedHub Team

'''

ADMIN_RESPONSE = "I would be more than happy to help you with that. Unfortunately, the person responsible for that is unavailable at the moment. We'll get back with you soon. Thanks."
