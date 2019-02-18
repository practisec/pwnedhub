## Session Management

| Vulnerability | Session token cookie missing the `HttpOnly` flag. |
| :-- | :-- |
| Location | `pwnedhub/config.py`: Configuration variables. |
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
| Location | `pwnedhub/views/*`: No cache control logic. |
| Remediation | Implement the proper cache control headers to prevent the caching of responses containing sensitive information. |

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

@app.route('/profile')
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
| Location | `pwnedhub/views/errors.py`: `internal_server_error` controller provides verbose output for 500 server error conditions. |
| Remediation | Only debug on the client in the development environment. Otherwise, store exception information on the server with an associated unique ID and pass the ID to the client for cross reference. |

| Vulnerability | Verbose response headers. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Result of the `add_header` function. |
| Remediation | Remove the declaration within the `add_header` function. |

| Vulnerability | Possible usernames in static content. |
| :-- | :-- |
| Location | `pwnedhub/templates/about.html`: Paragraph with handles that are actually usernames. |
| Remediation | Remove sensitive information from public access. |

---

## Injection

| Vulnerability | Command Injection (OSCI) using command substitution and line terminating characters. |
| :-- | :-- |
| Location | `pwnedhub/validators.py`: `is_valid_command` function does not account for command substitution and line terminating characters. |
| Remediation | Add the `` `$()\r\n`` characters to the blacklist. |

| Vulnerability | Server-Side Template Injection (SSTI) |
| :-- | :-- |
| Location | `pwnedhub/views/errors.py`: `not_found` controller concatenates raw user input with the template as a string. |
| Remediation | Send user input to the template context using the `render_template` function, which doesn't process input as raw template code. |

```
return render_template('404.html', message=request.url), 404
```

| Vulnerability | SQL Injection (SQLi) for authentication bypass. |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `login` controller builds a raw query by concatenating user input with existing SQL. |
| Remediation | Use the ORM as intended, or prepared statements/parameterized queries. |

```
        user = User.get_by_username(request.form['username'])
...
        if user and user.is_enabled:
...
            if user.check_password(request.form['password']):
```

| Vulnerability | Blind SQL Injection (SQLi) for data extraction (string type). |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `reset_init` controller builds a raw query by concatenating user input with existing SQL. |
| Remediation | Use the ORM as intended, or prepared statements/parameterized queries. |

```
user = User.get_by_username(request.form['username'])
```

| Vulnerability | Blind SQL Injection (SQLi) for data extraction (integer type). |
| :-- | :-- |
| Location | `pwnedhub/views/api.py`: `tool_read` controller builds a raw query by concatenating user input with existing SQL. |
| Remediation | Use the ORM as intended, or prepared statements/parameterized queries. |

```
# api.py
tool = Tool.query.get_or_404(tid)
return jsonify(**tool.serialize())

# models.py
def serialize(self):
    return {
        'id': self.id,
        'name': self.name,
        'path': self.path,
        'description': self.description,
    }
```

| Vulnerability | Blind SQL Injection (SQLi) for data extraction via SOAP web service (integer type). |
| :-- | :-- |
| Note | Discoverable and exploitable from an unauthenticated perspective. |
| Location | `pwnedhub/views/service.py`: `ToolsInfo` operation builds a raw query by concatenating user input with existing SQL. |
| Remediation | Use the ORM as intended, or prepared statements/parameterized queries. |

| Vulnerability | Mass Assignment to set the role of the registered user. |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `register` controller builds `user_dict` from `request.form`. |
| Remediation | Build the `user_dict` using explicitly named fields rather than trust all incoming parameters. |

| Vulnerability | Reflected Cross-Site Scripting (XSS) |
| :-- | :-- |
| Location | `pwnedhub/views/errors.py`: `not_found` controller concatenates raw user input with the template as a string. |
| Remediation | Send user input to the template context using the `render_template` function, which will enforce template context encoding. |

```
return render_template('404.html', message=request.url), 404
```

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML context. |
| :-- | :-- |
| Location | `pwnedhub/templates/messages.html`: Template context encoding disabled by the `\|safe` filter on the `message.comment` string. |
| Remediation | Remove the `\|safe` filter to properly encode for the HTML context. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML context. |
| :-- | :-- |
| Location | `pwnedhub/views/api.py`: `messages_read` controller sets the response's content type to `text/html`. |
| Remediation | Set the response's `Content-Type` header to match the content type of the response payload. |
| Note | This is done correctly by default in Flask and must be explicitly set incorrectly. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML context. |
| :-- | :-- |
| Location | `pwnedhub/templates/mail_view.html`: Template context encoding disabled by the `\|safe` filter on the `letter.content` string. |
| Remediation | Remove the `\|safe` filter to properly encode for the HTML context. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML context. |
| :-- | :-- |
| Location | `pwnedhub/templates/submission_view.html`: Template context encoding bypassed by the `\|markdown` filter on the `submission.description` and `submission.impact` strings. |
| Remediation | Disable pass-through HTML or add HTML encoding of the markdown code prior to rendering in the `markdown_filter` custom Jinja2 filter. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML context. |
| :-- | :-- |
| Location | `pwnedhub/templates/notes.html`: Client-side markdown renderer permits the pass-through of raw HTML. |
| Remediation | Disable pass-through HTML or add HTML encoding of the markdown code prior to rendering. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the HTML attribute context. |
| :-- | :-- |
| Location | `pwnedhub/templates/*.html`: Template context encoding disabled by the `\|safe` filter on the `*.avatar_or_default` string. |
| Remediation | Remove the `\|safe` filter to encode for the HTML context which in this case also prevents execution in the attribute context. |

| Vulnerability | Stored Cross-Site Scripting (XSS) in the JavaScript context. |
| :-- | :-- |
| Location | `pwnedhub/templates/notes.html`: `g.user.username` string used as the value for a JavaScript variable. |
| Remediation | Replace the `\|safe` filter with a custom filter that properly escapes for the JavaScript context. |

```
_js_escapes = {
    ord(u'\\'): u'\\u005C',
    ord(u'\''): u'\\u0027',
    ord(u'"'): u'\\u0022',
    ord(u'>'): u'\\u003E',
    ord(u'<'): u'\\u003C',
    ord(u'&'): u'\\u0026',
    ord(u'='): u'\\u003D',
    ord(u'-'): u'\\u002D',
    ord(u';'): u'\\u003B',
    ord(u'`'): u'\\u0060',
    ord(u'\u2028'): u'\\u2028',
    ord(u'\u2029'): u'\\u2029'
}

# escape every ASCII character with a value less than 32.
_js_escapes.update((ord(u'%c' % z), u'\\u%04X' % z) for z in range(32))

def escapejs(value):
    """hex encode characters for use in JavaScript strings."""
    return unicode(value).translate(_js_escapes)

from utils import escapejs
app.jinja_env.filters['escapejs'] = escapejs
```

| Vulnerability | DOM-based Cross-Site Scripting (D-XSS) |
| :-- | :-- |
| Location | `static/common.js`: Value of the `error` parameter parsed from `document.URL` and dynamically added to the flash element via JavaScript. |
| Remediation | Use the built-in `flash` function from Flask, populate the DOM using safe JavaScript functions or properties, or properly encode the output on the client-side. |

```
// JavaScript
flash.textContent = msg;

# Flask
flash('Invalid username or password.')
```

| Vulnerability | Cross-Site Request Forgery (CSRF) for privilege escalation. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Lack of CSRF protection for the `admin_users` controller. |
| Remediation | Implement anti-CSRF controls on the `admin_users` controller. |
| Note | Requires refactoring the `admin_users` controller to use `POST`, or passing the token as a header that must be processed and returned by the client. |

| Vulnerability | Cross-Site Request Forgery (CSRF) for lateral authorization bypass. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Lack of CSRF protection for the `profile_change` controller. |
| Remediation | Implement anti-CSRF controls on the `profile_change` controller. |

```
# in login view
session['csrf_token'] = 'thisisacryptographicallystrongtoken'

# in profile template
<input name="csrf_token" type="hidden" value="{{ session.csrf_token }}" />

# in profile_change view
if request.values['csrf_token'] == session.get('csrf_token'):

# decorator alternative
def csrf_protect(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if 'csrf_token' in request.values and request.values['csrf_token'] == session.get('csrf_token'):
            return func(*args, **kwargs)
        return abort(403)
    return wrapped

app.route('/profile/change', methods=['GET', 'POST'])
@login_required
@csrf_protect
def profile_change():
    ...
```

| Vulnerability | Cross-Site Request Forgery (CSRF) of a REST web service. |
| :-- | :-- |
| Location | `pwnedhub/views/api.py`: `messages_create` controller parses JSON from requests with mismatched content types, allowing the request to bypass preflighted CORS checks. |
| Remediation | Set the JSON parser to only parse requests with the proper JSON content type. |
| Note | This is done correctly by default in Flask and must be explicitly set incorrectly. |

```
jsonobj = request.get_json()
```

| Vulnerability | Method Interchange to simplify CSRF attacks against users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: `method` parameter of the route decorator for the `profile_change` controller. |
| Remediation | Remove `GET` from the list of allowed methods on the route decorator and access parameters via `request.form` rather than `request.values`. |

| Vulnerability | Arbitrary file upload. |
| :-- | :-- |
| Location | `pwnedhub/validators.py`: `is_valid_filename` and `is_valid_mimetype` functions. |
| Remediation | Enhance the filename validator to properly validate the file extension and validate the MIME-type via the file content's magic bytes rather than the untrusted `Content-Type` header. |

| Vulnerability | Path Traversal to upload files to any writable location. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: `os.path.join` function in the `artifacts_save` controller allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path (canonical path) or create an indirect mapping for all files. |

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Path Traversal to delete arbitrary files. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: `os.path.join` function in the `artifacts_delete` controller allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path (canonical path) or create an indirect mapping for all files. |

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Path Traversal to read arbitrary files. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: `os.path.join` function in the `artifacts_view` controller allows for path traversal. |
| Remediation | Use the `os.path.abspath` function to validate the final calculated path (canonical path) or create an indirect mapping for all files. |

```
unsafe_path = os.path.join(session.get('upload_folder'), filename)
if os.path.abspath(unsafe_path).startswith(session.get('upload_folder')):
    # continue
```

| Vulnerability | Open Redirect |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `login` controller redirects to `request.args.get('next')`. |
| Remediation | Validate the path of the `next` parameter and/or create an indirect mapping for specific resources. |

```
def is_safe_url(url, origin):
    host = urlparse(origin).netloc
    proto = urlparse(origin).scheme
    # reject blank urls
    if not url:
        return False
    url = url.strip()
    url = url.replace('\\', '/')
    # simplify down to proto://, //, and /
    if url.startswith('///'):
        return False
    url_info = urlparse(url)
    # prevent browser manipulation via proto:///...
    if url_info.scheme and not url_info.netloc:
        return False
    # no proto for relative paths, or a matching proto for absolute paths
    if not url_info.scheme or url_info.scheme == proto:
        # no host for relative paths, or a matching host for absolute paths
        if not url_info.netloc or url_info.netloc == host:
            return True
    return False
```

| Vulnerability | XML External Entity (XXE) processing enabled. |
| :-- | :-- |
| Location | `pwnedhub/views/api.py`: `artifacts` controller doesn't explicitly disable DTD processing. |
| Remediation | Explicitly disable DTD processing by setting the `resolve_entities=False` argument when instantiating the `XMLParser`. |

```
parser = etree.XMLParser(resolve_entities=False)
```

| Vulnerability | Server-Side Request Forgery (SSRF). |
| :-- | :-- |
| Location | `pwnedhub/views/api.py`: `unfurl` controller doesn't validate the provided `uri` as safe to unfurl. |
| Remediation | On the Application layer, disallow non-HTTP protocol handlers, disable redirects, and validate the provided `uri` to prevent the use of RFC 1918 addresses. Resolve hostnames to dot-decimal notation IP addresses prior to validation. Ensure that inconsistencies between URL parsers, DNS checkers, and URL requesters don't allow for the injection of CR-LF characters. On the Network layer, restrict inbound traffic from the server. |

---

## Authorization

| Vulnerability | Missing Function Level Access Control (MFLAC) to escalate/revoke other users' privileges (no self-modification allowed). |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Missing decorator for the `admin_users_modify` controller. |
| Remediation | Add the `@roles_required('admin')` decorator to the `admin_users_modify` controller. |
| Note | Basic users are redirected to the `admin_users` controller and receive a 403 after successful exploitation. |

| Vulnerability | Missing Function Level Access Control (MFLAC) to enable/disable other users' profiles. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Missing decorator for the `admin_users_modify` controller. |
| Remediation | Add the `@roles_required('admin')` decorator to the `admin_users_modify` controller. |
| Note | Basic users are redirected to the `admin_users` controller and receive a 403 after successful exploitation. |

| Vulnerability | Insecure Direct Object Reference (IDOR) to read other users' mail. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Lack of receiver validation in the `mail_view` controller. |
| Remediation | Ensure that the provided mail `id` belongs to the owner of the session by comparing the current user to the mail's receiver. |

```
...
if letter.receiver == g.user:
...
```

| Vulnerability | Insecure Direct Object Reference (IDOR) to reply to other users' mail. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Lack of receiver validation in the `mail_reply` controller. |
| Remediation | Ensure that the provided mail `id` belongs to the owner of the session by comparing the current user to the mail's receiver. |

```
...
if letter.receiver == g.user:
...
```

| Vulnerability | Insecure Direct Object Reference (IDOR) to delete other users' mail. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: Lack of receiver validation in the `mail_delete` controller. |
| Remediation | Ensure that the provided mail `id` belongs to the owner of the session by comparing the current user to the mail's receiver. |

```
...
if letter.receiver == g.user:
...
```

| Vulnerability | No re-authentication required for state-changing operations. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: No logic in the `profile_change` controller requiring the user to authenticate prior to processing the request. |
| Remediation | Add a current password field that must be validated against the target profile before processing the request. |

---

## Data Storage

| Vulnerability | Passwords stored in plain text or reversible form. |
| :-- | :-- |
| Location | `pwnedhub/pwnedhub/models.py`: `xor_encrypt` used to set the password in the `User` model.  |
| Remediation | Modify the `User` model to use an Adaptive Hashing algorithm (e.g. bcrypt) as opposed to encryption. |
| Note | Evidenced by the `password` field in the profile view containing the clear text password. Changing the password storage mechanism requires careful consideration of how to handle existing passwords. |

---

## Authentication

| Vulnerability | User Enumeration to validate possible usernames. |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `register` controller responds with a unique error for existing usernames. |
| Remediation | Create a registration system that responds with a generic message, uses the email address as the username (unique key), and requires out-of-band verification. |

| Vulnerability | User Enumeration to validate possible usernames. |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: `reset_init` controller responds with a unique error for existing usernames. |
| Remediation | Create a reset system that responds with a generic message and requires out-of-band verification. |
| Note | This remediation assumes that the application uses an email address as the username (unique key). |

| Vulnerability | Weak password complexity requirement. |
| :-- | :-- |
| Location | `pwnedhub/validators.py`: `is_valid_password` function. |
| Remediation | Enhance the validator to enforce something more than a minimum length of 1 character. |

```
# 1 upper, 1 lower, 1 special, 1 number, minimum 10 chars
PASSWORD_REGEX = r'(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*\(\)]).{10,}'
# 15 more more characters
PASSWORD_REGEX = r'.{15,}'
```

| Vulnerability | Users permitted to use words related to the application in their passwords. |
| :-- | :-- |
| Location | `pwnedhub/templates/about.html`: Paragraph with nicknames. |
| Remediation | Prevent users from using words related to the application in their passwords. |

```
blacklist = ['PwnedHub', 'collaborate']
if any(word.lower() in password.lower() for word in blacklist):
    return False
```

---

## Logic Flaws

| Vulnerability | Arbitrary access to the operating system. |
| :-- | :-- |
| Location | `pwnedhub/views/core.py`: `admin_tools_add` controller permits an administrator to add any command supported by the operating system to the tools page. |
| Remediation | Apply a whitelist filter of eligible commands to restrict which tools can be added to the application's interface. |

| Vulnerability | Flow control weakness allows for reset of arbitrary users' passwords. |
| :-- | :-- |
| Location | `pwnedhub/views/auth.py`: Once an attacker submits a valid username in the first step of the password reset flow, they can directly request the reset password endpoint to bypass the security question step because the `reset_password` controller doesn't enforce flow control. |
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

| Vulnerability | Manipulation of the bounty scoring system via bypassing data similarity checks. |
| :-- | :-- |
| Location | The application uses a data similarity check to prevent reviewers from resubmitting assigned bugs in an effort to have them accepted by another reviewer without accepting the bug for the original submitter. However, the data similarity check uses a Jaccard similarity algorithm that can be bypassed by adding a bunch of random words to the submission to lower the similarity score. |
| Remediation | Educate reviewers about the danger of anything out of place in a submission, such as groups of random words. Use a better algorithm to conduct similarity checks. |

| Vulnerability | Manipulation of the bounty scoring system via bypassing data similarity checks. |
| :-- | :-- |
| Location | The application uses a data similarity check to prevent reviewers from resubmitting assigned bugs in an effort to have them accepted by another reviewer without accepting the bugs for the original submitters. However, the data similarity check only occurs when a bug is submitted, and not when it is edited. Therefore, a reviewer may still conduct this attack by submitting garbage to bypass the new submission data similarity check, then quickly modify the submission to be a copy of the valid bug before the new reviewer sees it. |
| Remediation | Conduct data similarity checks for edited submissions in addition to new submissions. |

| Vulnerability | Manipulation of the bounty scoring system via open registration. |
| :-- | :-- |
| Location | Any user can create dummy accounts, submit invalid bugs repeatedly from their real account, and accept any bugs that get randomly assigned to a dummy account for review. |
| Remediation | Penalize rejections, validate new users as unique before allowing them to contribute to the bug bounty system, or replace the self-registration system with an invite only system. |
| Note | Exploitation requires avoiding data similarity checks, but this should be trivial since the submissions are junk data. |

---

## Miscellaneous

| Vulnerability | Outdated client-side software. |
| :-- | :-- |
| Location | `pwnedhub/static/jquery-1.6.2.min.js`: `pwnedhub/templates/layout.html` template references an old version of jQuery. |
| Remediation | Update the jQuery library and associated import statement in `pwnedhub/templates/layout.html`. |

```
<script type="text/javascript" src="{{ url_for('static', filename='js/jquery-latest.min.js') }}"></script>
```

| Vulnerability | User Interface Redressing. |
| :-- | :-- |
| Location | `pwnedhub/views/*`: No framing prevention logic. |
| Remediation | Implement the proper headers to prevent the application from being framed by untrusted third parties. |

```
# affects all views
@app.after_request
def add_header(response):
    response.headers["X-Frame-Options"] = "DENY"
    # Other safe values:
    # SAMEORIGIN
    # ALLOW-FROM https://trusted.com/
    # or
    response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
    # Other safe values:
    # frame-ancestors 'self'
    # frame-ancestors trusted.com
    return response

# decorator for specific views
def no_frame(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        response = make_response(func(*args, **kwargs))
        response.headers["X-Frame-Options"] = "DENY"
        # or
        response.headers["Content-Security-Policy"] = "frame-ancestors 'none'"
        return response
    return wrapped

@app.route('/profile')
@no_frame
def profile():
    ...
```

---
