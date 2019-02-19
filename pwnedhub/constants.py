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

BUG_NOTIFICATIONS = {
    1: "We regret to inform you that your submission (<a href='{}'>bug ID #{:05d}</a>) has been rejected. For additional feedback, please contact the assigned reviewer. Thank you for your participation.",
    2: "Congratulations! Your submission (<a href='{}'>bug ID #{:05d}</a>) has been confirmed as a valid bug. The bug has been disclosed to the public and your profile has been awarded {} reputation points. Thank you for being a valuable member of the PwnedHub community!",
    3: "This is a courtesy email to inform you that your submission (<a href='{}'>bug ID #{:05d}</a>) has been fixed. Thank you again for being a valuable member of the PwnedHub community!",
}

REVIEW_NOTIFICATION = "You've been randomly selected to review a bug bounty submission. That means that you are eligible to receive 25% of the bounty allotted for an accepted review of this bug! Please visit the submission page for <a href='{}'>bug ID #{:05d}</a> to review the submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!"

UPDATE_NOTIFICATION = "A submission for which you are the reviewer has been updated. Please visit the submission page for <a href='{}'>bug ID #{:05d}</a> to review the updated submission and accept/reject accordingly. Thank you for being a valuable member of the PwnedHub community!"

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

DEFAULT_NOTE = '''##### Welcome to PwnedHub!

A consolidated bug bounty and hosted scanning platform. Below are some things you can do here:

**Find flaws.**

* This is your notes space. Keep your personal notes here.
* Store artifacts from local and external tools in the artifacts space.
* Leverage popular security testing tools right from your browser in the tools space.

**Submit bugs.**

* Check your position in one of several categories in the scoreboard space.
* Review bugs for validation or perusal in the submissions space.
* Submit new bugs for bounties in the new submission space.

**Collect bounties.**

* Privately discuss submissions with submitters and reviewers in the pwnmail space.
* Share public information and socialize in the messages space.

Happy hunting!

\- The PwnedHub Team

'''

ADMIN_RESPONSE = "I would be more than happy to help you with that. Unfortunately, the person responsible for that is unavailable at the moment. We'll get back with you soon. Thanks."
