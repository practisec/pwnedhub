# Preferences

- Keep styles consistent between applications.
- Keep coding techniques and structure consistent between applications.

# PwnedHub

PwnedHub is an **intentionally vulnerable** web application for [PractiSec](https://www.practisec.com/training/) security training courses. Vulnerabilities are features, not bugs. Do not fix security issues unless explicitly asked.

## Do Not "Fix" These (They're Intentional)

- XOR password encryption (`utils.py:xor_encrypt/xor_decrypt`)
- Configurable SQL injection, command injection, CSRF, and CORS protections
- `SESSION_COOKIE_HTTPONLY = False` in pwnedhub
- Hardcoded database credentials in config files
- 100ms timing side-channel on valid usernames (`pwnedhub/routes/auth.py`)
- JWT signature verification that can be toggled off via admin panel

When adding new features, match the existing security posture. Don't add protections the rest of the codebase doesn't have.

## Services

Six Flask apps behind an Nginx reverse proxy, all Docker Compose:

| Service | Domain | What it does |
|---------|--------|-------------|
| pwnedhub | www.pwnedhub.com | Main app. Server-rendered Jinja2 templates, session auth. |
| pwnedapi | api.pwnedhub.com | REST API (Flask-RESTful) + WebSockets (Socket.IO/gevent). JWT auth. |
| pwnedspa | test.pwnedhub.com | Vue 3 SPA frontend that talks to pwnedapi. No build step (browser ES modules). |
| pwnedsso | sso.pwnedhub.com | OIDC/SSO provider. Issues JWTs consumed by pwnedhub and pwnedapi. |
| pwnedadmin | admin.pwnedhub.com | Toggles security controls + webmail inbox for out-of-band emails. |
| adminbot | (no web UI) | Selenium/Firefox bot. Triggered via Redis queue to simulate admin actions. |

## How Services Talk to Each Other

- **Shared admin database:** pwnedhub, pwnedapi, and pwnedadmin all connect to the `pwnedhub-admin` MySQL database via `__bind_key__ = 'admin'`. The `Config` model is duplicated in each service's `models.py`. When pwnedadmin toggles a flag, the other services read it on the next request via `Config.get_value(name)`.
- **Redis queues:** pwnedhub enqueues `adminbot-tasks` jobs when users mail the admin. pwnedapi enqueues `pwnedapi-tasks` for async scans. The adminbot worker and api-worker containers listen on their respective queues.
- **Auth flows:** pwnedhub redirects to pwnedsso for login, which returns a JWT. For Google OAuth, pwnedhub handles the OAuth dance and redirects back to pwnedspa with an id_token that pwnedapi validates.
- **No shared Python code.** Each service has its own models, utils, and decorators with some duplication. The only shared thing is `common/static/` (images, fonts) mounted as a Blueprint via relative path `../common/static`.

## Things That Will Bite You

**Docker:**
- `~/tmp:/tmp` volume mount is critical. Sessions (FileSystemCache at `/tmp/sessions`), file uploads (`/tmp/artifacts`), and inter-container file sharing all depend on it.
- Database is NOT persisted across `docker compose down`. All data resets.
- `depends_on` only controls startup order, not readiness. Services may fail to connect if MySQL isn't ready yet.

**Base image + runtime deps:**
- A single shared Dockerfile (`./Dockerfile`) builds `pwnedhub-base` from `ubuntu:22.04` (kept close to the AWS EC2 Ubuntu AMI). It bakes the common OS/system layer: Python 3.10, build tools, `libmariadb-dev`, an upgraded pip, `/etc/my.cnf`, Firefox, and `WORKDIR /src`. The `app` service carries the `build:`; every other app service just references `image: pwnedhub-base`. Build with `docker compose build` (or `docker compose up --build`).
- Application Python deps are NOT baked. Each service's `command:` runs `pip install -r <service>/REQUIREMENTS.txt` then the gunicorn/rq command, so per-app requirements stay separate and a dependency change just needs a restart (source is hot-mounted at `/src`). apt does not run at container start — only pip — so startup is quick once the base is built.
- `command:` needs a shell for the `&&`, so it's `sh -c "<script>"` (the list form `["sh","-c","<script>"]` is equivalent). A bare string `command:` gets shlex-split into argv and run WITHOUT a shell, so `&&` would become a literal arg. `sh -c "…"` as a single string shlex-splits correctly because the quotes keep the script as one token.
- MySQL client lib is **`libmariadb-dev`**, NOT `default-libmysqlclient-dev`. On Ubuntu the latter pulls Oracle's `libmysqlclient`, which rejects the `mysql` server's `caching_sha2_password` auth over a non-TLS connection; MariaDB's Connector/C auto-fetches the server public key and connects. (The `/etc/my.cnf` `ssl=0` baked into the base is a no-op — the app's connection URI doesn't read option files — but is kept for parity with the old images.)
- The base upgrades pip because Ubuntu 22.04's stock pip (22.0.2) is too old to build `mysqlclient`'s sdist metadata (fails with a "name unknown" error).
- Firefox comes from Mozilla's apt repo — jammy's `firefox` apt package is a snap that won't run in a container. Only the bot uses it, but it lives in the shared base (layer-shared, so cheap) so nothing installs packages at runtime. **geckodriver is baked into the base too** (arch-detected `linux-aarch64`/`linux64`, at `/usr/bin/geckodriver`), NOT fetched by Selenium Manager at runtime: Selenium ships no Selenium Manager binary for `linux/aarch64`, so on Apple Silicon the runtime locator can't run at all — even with geckodriver on `PATH` it fails, because Selenium Manager throws before it consults `PATH`. `adminbot/bot.py` passes `executable_path='/usr/bin/geckodriver'` to `FirefoxService`, which skips Selenium Manager entirely (inert on x86 prod, required on arm64).
- Alpine→Ubuntu deps: `build-base`→`build-essential`+`python3-dev`; `libxslt-dev`/`libffi-dev` dropped (lxml/cryptography/gevent install as manylinux wheels on glibc — only `mysqlclient` still compiles).
- nginx caches upstream IPs at startup. If you recreate an app service without recreating `proxy`, you'll get 502s from stale IPs — `docker compose restart proxy`. A full fresh `up` starts `proxy` last (via `depends_on`), so it only bites on selective recreate.
- **Upgrade rehearsal:** this setup mirrors production so the next Ubuntu LTS can be worked out here first. Bump the `FROM` tag in `./Dockerfile` and rebuild — OS/system conflicts (Python bump, PEP 668, library changes) surface at base-build time in one place; pinned-dependency conflicts (e.g. no wheel for the new Python) surface at per-service pip install. Note 24.04 ships a PEP 668 "externally-managed" marker, so root `pip install` into system site-packages will need a venv or `--break-system-packages`.

**pwnedapi workers:**
- Must use `--workers 1 --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker` for Socket.IO to work. Standard gunicorn workers break WebSockets. (See `docker-compose.yaml`.)
- Nginx has special WebSocket upgrade config in `proxy/nginx.conf` for the `/socket.io` path.

**WebSocket sessions:**
- `g` doesn't persist across Socket.IO events, so session stores the authenticated user. After any `db.session.commit()` in websocket handlers, re-fetch the user object or equality comparisons break (see `pwnedapi/routes/websockets.py`).

**Common static Blueprint:**
- Uses relative path `../common/static` from each service's directory. Depends on `WORKDIR /src` (set in the base `Dockerfile`) so gunicorn imports `<service>.wsgi` from `/src` and the blueprint resolves `../common/static` as `/src/common/static`.

**Selenium bot:**
- Has a monkey patch for broken Firefox logging (`adminbot/bot.py`). Will need updating if Selenium is upgraded.
- Uses a workaround for clicking `<tr>` elements (clicks first child `<td>` instead).

**CORS:**
- Whitelist is hardcoded to `www.pwnedhub.com` and `test.pwnedhub.com` in pwnedapi. Adding new domains requires updating this.
- CSRF token headers differ: pwnedapi uses `X-Csrf-Token`, pwnedhub uses session-based CSRF tokens.

## Running It

```
docker compose build       # builds the shared pwnedhub-base image (first run / after Dockerfile changes)
docker compose up          # add -d for daemon mode; use --build to build+up in one step
docker compose down
```

The build produces one shared `pwnedhub-base` image (Ubuntu + system libs + Python + pip + Firefox); it needs network and takes a few minutes the first time. After that, each service only pip-installs its own `REQUIREMENTS.txt` at start, so `up` is quick.

Requires `/etc/hosts` entries:
```
127.0.0.1   www.pwnedhub.com sso.pwnedhub.com test.pwnedhub.com api.pwnedhub.com admin.pwnedhub.com
```

Database can be re-initialized inside containers with `flask init [dataset]`, `flask export`, or `flask purge`.

## Where Things Live

- **Routes:** `<service>/routes/` — blueprints registered in `<service>/__init__.py`
- **Models:** `<service>/models.py` — SQLAlchemy declarative models
- **Config:** `<service>/config.py` — BaseConfig/Development/Production classes, selected by `CONFIG` env var
- **Auth decorators:** `pwnedhub/decorators.py` (`@login_required`, `@roles_required`, `@csrf_protect`) and `pwnedapi/decorators.py` (`@token_auth_required`, `@validate_json`)
- **Vue SPA:** `pwnedspa/static/vue/` — views, components, stores (Pinia), router
- **DB init scripts:** `database/init/01-04*.sql` — run once on first MySQL container start
- **Nginx config:** `proxy/nginx.conf` — hostname-based routing to services
- **Docker:** `docker-compose.yaml` + a single `Dockerfile` at the repo root that builds the shared `pwnedhub-base` image all app services run from (see "Base image + runtime deps" below). No per-service Dockerfiles.

## Databases

| Database | Used by | Contains |
|----------|---------|----------|
| pwnedhub | pwnedhub, pwnedsso | Users, messages, notes, tools, mail, tokens |
| pwnedhub-test | pwnedapi | Same schema, separate data for API service |
| pwnedhub-admin | pwnedhub, pwnedapi, pwnedadmin | Config flags, email queue |

All accessed by MySQL user `pwnedhub`/`dbconnectpass`. The admin database is bound via `SQLALCHEMY_BINDS`, not the default connection.

## Tests

There is a pytest suite covering four of the services, run inside the Docker containers via `./run_tests.sh` (passes `-v` by default; forward other pytest args, e.g. `./run_tests.sh -k scan`). Each service runs with `CONFIG=Test` against an in-memory SQLite database seeded in its `conftest.py`.

`run_tests.sh` uses `docker compose exec`, so **the stack must be up first** (`docker compose up -d`). The base image bakes no app/test deps; each service's `command:` pip-installs its `REQUIREMENTS.txt` plus `pytest` at startup, so tests run against the already-installed live container. (A fresh `docker compose run` would not have them — it overrides the `command:`.)

| Suite | Tests | Covers |
|-------|-------|--------|
| `tests/pwnedhub` | 65 | Routes, auth, admin, mail/messages/notes, tools, and vulnerability behaviors |
| `tests/pwnedapi` | 40 | REST resources + vulnerability tests (SQLi, JWT bypass, SSRF, IDOR, mass assignment, expression-language injection) |
| `tests/pwnedsso` | 4 | SSO authenticate endpoint |
| `tests/pwnedadmin` | 7 | Config toggle + webmail inbox routes |

Notes:
- The pwnedapi suite mocks Redis and the RQ task queues (`conftest.py`), so the real RQ `Job` API is not exercised — queue-boundary regressions won't be caught.
- There is no linting configuration and no CI/CD pipeline; tests are run manually.
