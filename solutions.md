## Session Management

| Vulnerability | Session token cookie missing the `HttpOnly` flag. |
| :-- | :-- |
| Location | `pwnedhub/__init__.py`: Configuration variables. |
| Remediation | Set the `SESSION_COOKIE_HTTPONLY` configuration variable to `True`. |

```
...
SESSION_COOKIE_HTTPONLY = True
...
```

---

## Information Disclosure

| Vulnerability | Sensitive data persisted on the client in `localStorage`. |
| :-- | :-- |
| Location | `pwnedhub/templates/notes.html`: JavaScript uses `localStorage` to persist potentially sensitive information in the browser. |
| Remediation | Use `sessionStorage` instead of `localStorage` or clear `localStorage` `onunload`. |

```
sessionStorage.setItem(key, value)
// or
localStorage.removeItem(key);
// or
localStorage.clear()
```

| Vulnerability | No cache protection. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: No cache control logic. |
| Remediation | Implement the proper cache control headers to prevent the caching of sensitive information. |

Example:

```
# affects all views
@app.after_request
def add_header(response):
    ...
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response

# decorator for specific views
def no_cache(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Expires'] = '0'
        return response
    return wrapped

@app.route('/profile/<int:uid>')
@no_cache
def profile(uid):
    ...
```

| Vulnerability | Verbose `robots.txt` file. |
| :-- | :-- |
| Location | `pwnedhub/static/robots.txt`: Entry in the list of disallowed resources. |
| Remediation | Remove from the list and implement proper access controls. |

| Vulnerability | Verbose error reporting. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `internal_error` view provides verbose output for 500 server error conditions. |
| Remediation | Remove this functionality and only debug in the development environment. |

| Vulnerability | Verbose response headers. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Result of the `add_header` view. |
| Remediation | Remove the declaration within the `add_header` function. |

| Vulnerability | Possible usernames in static content. |
| :-- | :-- |
| Location | `pwnedhub/templates/about.html`: Paragragh with nicknames. |
| Remediation | Remove sensitive information from public access. |

---

## Injection

| Vulnerability | Command Injection (OSCI) using command substitution. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: `re.sub('[;&|]', '', cmd)` in the `tools_execute` view does not account for command substitution characters. |
| Remediation | Add the `` `$()`` characters to the blacklist. |

| Vulnerability | Command Injection (OSCI) by adding commands via the admin interface and leveraging the tools page. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Result of the `admin_tools` view. |
| Remediation | Restrict which tools administrators can add to the application. |

| Vulnerability | Server-Side Template Injection (SSTI) |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `page_not_found` view appends raw user input to a template string using string formating. |
| Remediation | Send user input to the tempate context using the `render_template_string` function, which doesn't process input as raw template code. |

Example:

```
return render_template('404.html', message=request.url), 404
```

| Vulnerability | SQL Injection (SQLi) for authentication bypass. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Raw query built with user input via string formatting/concatenation in the `login` view. |
| Remediation | Use the ORM as intended, or prepared statements/parameterized queries. |

Example:

```
        user = User.get_by_username(request.form['username'])
...
        if user and user.is_enabled:
...
            if user.check_password(request.form['password']):
```

| Vulnerability | SQL Injection (SQLi) for data extraction via SOAP web service. |
| :-- | :-- |
| Note | Discoverable and exploitable from an unathenticated perspective. |
| Location | `pwnedhub/views.py`: The `info` view builds a raw query with raw user input via string formatting/concatenation. |
| Remediation | Use the ORM as intended, prepared statements/parameterized queries, or sanitize input to remove malicious characters. |

| Vulnerability | SQL Injection (SQLi) for data extraction. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `tools_info` view builds a raw query with raw user input via string formatting/concatenation. |
| Remediation | Use the ORM as intended, prepared statements/parameterized queries, or sanitize input to remove malicious characters. |

| Vulnerability | Mass Assignment to set the role of the registered user. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `register` view builds `user_dict` from `request.form`. |
| Remediation | Build the `user_dict` using explicitly named fields rather than trust all incoming parameters. |

| Vulnerability | Stored Cross-Site Scripting (XSS) |
| :-- | :-- |
| Location | `pwnedhub/templates/messages.html`: `|safe` filter used on the `message.comment` string. |
| Remediation | Remove the `|safe` filter to properly encode for the HTML context. |

| Vulnerability | DOM-based Cross-Site Scripting (D-XSS) |
| :-- | :-- |
| Location | `static/common.js`: Value of the `error` parameter parsed from `document.URL` and dynamically added to the page. |
| Remediation | Use the builtin `flash` function from Flask, populate the DOM using safe JavaScript functions or properties, or properly encode the output on the client-side. |

Example:

```
// JavaScript
flash.textContent = msg;

# Flask
flash('Invalid username or password.')
```

| Vulnerability | Reflected Cross-Site Scripting (XSS) |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `page_not_found` view appends raw user input to a template string using string formating. |
| Remediation | Send user input to the tempate context using the `render_template_string` function, which will enforce template context encoding. |

Example:

```
return render_template('404.html', message=request.url), 404
```

| Vulnerability | Cross-Site Request Forgery (CSRF) for privilege escalation. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Lack of CSRF protection for the `admin_users` view. |
| Remediation | Implement anti-CSRF controls on the `admin_users` view. |

| Vulnerability | Cross-Site Request Forgery (CSRF) for lateral authorization bypass. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Lack of CSRF protection for the `profile_change` view. |
| Remediation | Implement anti-CSRF controls on the `profile_change` view. |

| Vulnerability | Method Interchange to simplify CSRF attacks against users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: `method` parameter of the route decorator for the `profile_change` view. |
| Remediation | Remove `GET` from the list of allowed methods on the route decorator. |

| Vulnerability | Weak input validation allowing upload of any type of file. |
| :-- | :-- |
| Location | `pwnedhub/validators.py`: `is_valid_file` function. |
| Remediation | Enhance the validator to properly validate the file extension and MIME-typ via magic bytes. |

| Vulnerability | Path Traversal to upload files to any writeable location. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `os.path.join` function in the `artifacts_save` view allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path, create an indirect mapping for all files, or sanitize input to remove malicious characters. |

Example:

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Path Traversal to delete arbitrary files. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `os.path.join` function in the `artifacts_delete` view allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path, create an indirect mapping for all files, or sanitize input to remove malicious characters. |

Example:

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Path Traversal to read arbitrary files. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `os.path.join` function in the `artifacts_view` view allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path, create an indirect mapping for all files, or sanitize input to remove malicious characters. |

Example:

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Weak input sanitization allowing arbitrary access to the operating system. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `admin_tools_add` view doesn't limit the commands available for configuration. |
| Remediation | Apply a whiltelist filter of eligible commands. |

| Vulnerability | Open Redirect |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `login` view redirects to `request.args.get('next')`. |
| Remediation | Validate the path of the `next` parameter and/or create an indirect mapping for specific resources. |

```
def is_safe_url(url, origin):
    host = urlparse(origin).netloc
    proto = urlparse(origin).scheme
    if not url:
        return False
    url = url.strip()
    url = url.replace('\\', '/')
    if url.startswith('///'):
        return False
    url_info = urlparse(url)
    if not url_info.scheme or url_info.scheme == proto:
        if not url_info.netloc or url_info.netloc == host:
            return True
    return False
```

---

## Authorization

| Vulnerability | Missing function level access control. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Missing decorator for the `admin_users` view. |
| Remediation | Add the `@roles_required('admin')` decorator to the `admin_users` view. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to escalate privileges for other users (no self-modification allowed). |
| :-- | :-- |
| Note | Basic users are redirected and receive a 403 after successful exploitation. |
| Location | `pwnedhub/views.py`: Missing decorator for the `admin_users` view. |
| Remediation | Add the `@roles_required('admin')` decorator to the `admin_users` view. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to disable other users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Missing decorator for the `admin_users` view. |
| Remediation | Add the `@roles_required('admin')` decorator to the `admin_users` view. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to view other users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Lack of user validation in the `profile` view. |
| Remediation | Ensure that the requested `uid` belongs to the owner of the session by comparing it to the `user_id` stored in the session. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to change other users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Lack of user validation in the `profile_change` view. |
| Remediation | Ensure that the requested `uid` belongs to the owner of the session by comparing it to the `user_id` stored in the session. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to remove other users' messages. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: Lack of user validation in the `messages_delete` view. |
| Remediation | Ensure that the requested `uid` belongs to the owner of the session by comparing it to the `user_id` stored in the session. |

| Vulnerability | No re-authentication required for state-changing operations. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: No logic in the `profile_change` view requiring the user to authenticate prior to processing the request. |
| Remediation | Add a password field that must be validated against the target profile before processing the request. |

---

## Data Storage

| Vulnerability | Passwords stored in plain text or reversable form. |
| :-- | :-- |
| Location | `pwnedhub/templates/profile.html`: `password` field contains the password. |
| Remediation | Modify the `User` model to use an Adaptive Hashing algorithm (e.g. bcrypt) as opposed to encryption (XOR). |
| Note | Changing the password storage mechanism requires careful consideration of how to handle existing passwords. |

---

## Authentication

| Vulnerability | User Enumeration to validate possible usernames. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `register` view responds with a unique error for existing usernames. |
| Remediation | Create a registration system that uses the email address as the unique key (username) and requires out-of-band verification. |

| Vulnerability | User Enumeration to validate possible usernames. |
| :-- | :-- |
| Location | `pwnedhub/views.py`: The `reset_init` view responds with a unique error for existing usernames. |
| Remediation | Create a reset system that requires out-of-band verification instead of security questions, and responds with a generic message. |

| Vulnerability | Weak password complexity requirement. |
| :-- | :-- |
| Location | `pwnedhub/validators.py`: `is_valid_password` function. |
| Remediation | Enhance the validator to enforce something more than a minimum length of 1 character. |

Example:

```
# 1 upper, 1 lower, 1 special, 1 number, minimim 10 chars
PASSWORD_REGEX = r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*\(\)]).{10,}'
# 15 more more characters
PASSWORD_REGEX = r'.{15,}'
```

| Vulnerability | Users permitted to use words related to the application in their passwords. |
| :-- | :-- |
| Location | `pwnedhub/templates/about.html`: Paragragh with nicknames. |
| Remediation | Prevent users from using words related to the application in their passwords. |

Example:

```
blacklist = ['PwnedHub', 'collaborate']
if any(word.lower() in password.lower() for word in blacklist):
    return False
```

---

## Flow Control

| Vulnerability | Logic flaw to reset arbitrary users' passwords. |
| :-- | :-- |
| Note | Once an attacker submits a valid username in the first step of the password reset flow, they can directly request the reset password endpoint to bypass the security question step. |
| Location | `pwnedhub/views.py`: The `reset_password` view doesn't enforce flow control. |
| Remediation | Incorporate better flow control to ensure that the next step is not available until the previous step is complete. |

```
# recovery states
# 0: none
# 1: initialized
# 2: answered

# on login
session['recovery_state'] = 0

# for each step
if session['recovery_state'] != <expected state>:
    session['recovery_state'] = 0
    return render_template('reset_password.html')
...
session['recovery_state'] = <new state>
...
```

---

## Miscellaneous

| Vulnerability | Outdated Software |
| :-- | :-- |
| Location | `pwnedhub/static/jquery-1.6.2.min.js`: The `pwnedhub/templates/layout.html` template references an old version of jQuery. |
| Remediation | Update the jQuery library and associated import statement in `pwnedhub/templates/layout.html`. |

Example:

```
<script type="text/javascript" src="{{ url_for('static', filename='jquery-latest.min.js') }}"></script>
```

---
