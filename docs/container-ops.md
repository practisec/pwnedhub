# PwnedHub — Container Operations

Two self-contained playbooks. Use the one that matches your environment — each stands on its own:

- **[Dev](#dev)** — the local `docker compose` stack.
- **[Prod](#prod)** — the EC2 AMI deployment (systemd-managed, production overlay).

---

# Dev

The local stack from `docker-compose.yaml`. Source is hot-mounted at `/src`, each service pip-installs its `REQUIREMENTS.txt` at startup, and the database is **ephemeral** — it is destroyed on `docker compose down` and reseeded from `database/init/` on the next `up`. Run all commands from the repo root.

## Services

| Service | Domain | Role |
|---------|--------|------|
| `proxy` | `:80` | nginx reverse proxy — routes by `Host` to the app services |
| `app` | www.pwnedhub.com | Main server-rendered app (Jinja2, session auth) |
| `sso` | sso.pwnedhub.com | OIDC/SSO provider |
| `spa` | test.pwnedhub.com | Vue SPA frontend |
| `api` | api.pwnedhub.com | REST API + WebSockets (JWT) |
| `admin` | admin.pwnedhub.com | Security-control toggles + webmail inbox |
| `api-worker` | — | RQ worker for async scans — runs the security tools |
| `bot-worker` | — | Selenium adminbot (Firefox/geckodriver) |
| `db` | — | MySQL |
| `redis` | — | Redis (RQ queues) |

## Stack lifecycle

```bash
docker compose up -d              # start the stack (add --build after Dockerfile changes)
docker compose ps                 # status
docker compose restart app        # restart one service (picks up hot-mounted source edits)
docker compose restart proxy      # after recreating an app service (nginx caches upstream IPs)
docker compose down               # stop and remove — DESTROYS the database
```

## Logs

```bash
docker compose logs                     # all services
docker compose logs -f api              # follow one service
docker compose logs --tail=100 app      # last 100 lines
docker compose logs --since=10m api-worker
docker compose logs -f api-worker       # watch scans execute
docker compose logs -f bot-worker       # watch the adminbot
docker compose exec bot-worker tail -f /tmp/rq-geckodriver.log   # Firefox/geckodriver trace
```

## Inspect

```bash
docker compose ps                       # running services + ports
docker stats                            # live CPU/mem per container
docker compose images                   # image per service
docker inspect $(docker compose ps -q api)
docker network inspect pwnedhub_default # service network / aliases
```

## Shell / exec

```bash
docker compose exec app bash                                  # shell in a running container
docker compose run --rm --no-deps --entrypoint bash app       # throwaway container (no deps installed)
docker compose exec api python3                               # Python REPL
docker compose exec app flask <command>                       # app CLI (init/export/purge)
```

## Databases & queues

```bash
docker compose exec db mysql -uroot -padminpass                    # MySQL shell
docker compose exec db mysql -uroot -padminpass pwnedhub           # a specific database
docker compose exec redis redis-cli                                # Redis shell
docker compose exec redis redis-cli LLEN pwnedapi-tasks            # scan queue depth
docker compose exec redis redis-cli LLEN adminbot-tasks            # adminbot queue depth
```

## Verify the security tools

```bash
docker compose exec api-worker sh -c 'dig -v; nmap --version | head -1; nikto -Version | head -1; sqlmap --version; sslyze --version'
```

## Reset / reseed

The dev database is not persisted, so the simplest reset is a full recycle — `down` wipes it and `up` reseeds from `database/init/` via the MySQL init scripts:

```bash
docker compose down && docker compose up -d
```

To reseed in place (or to load the CTF dataset) without recycling:

```bash
docker compose exec -T db mysql -uroot -padminpass pwnedhub       < database/init/02-pwnedhub.sql
docker compose exec -T db mysql -uroot -padminpass pwnedhub-test  < database/init/03-pwnedhub-test.sql
docker compose exec -T db mysql -uroot -padminpass pwnedhub-admin < database/init/04-pwnedhub-admin.sql
docker compose exec -T app find /tmp/artifacts -mindepth 1 -delete
docker compose exec -T redis redis-cli FLUSHALL
docker compose restart app sso spa api api-worker admin bot-worker
```

Use `database/ctf/*.sql` for the CTF dataset. App-native alternative (fixtures): `docker compose exec <app> flask purge && docker compose exec <app> flask init <dataset>` for each of `app`/`api`/`admin`, where `<dataset>` is a fixtures subdirectory (`base`, `cs`, `ctf`).

## Rebuild after base-image or code changes

```bash
docker compose build                                # rebuild the shared pwnedhub-base image
docker compose up -d                                # recreate services off the new image
docker compose restart proxy                        # refresh nginx upstream IPs
docker compose up -d --force-recreate api-worker    # force-recreate a single service
```

---

# Prod

The stack runs on the EC2 AMI as a systemd-managed `docker compose` deployment in `/srv/pwnedhub`, using the production overlay (`docker-compose.prod.yaml`): per-service images with dependencies baked in, `restart: unless-stopped`, and **persistent** named volumes for MySQL (`dbdata`) and uploaded artifacts (`artifacts`). The database survives restarts and reboots.

SSH in, become root, and set up your shell — the commands below assume this:

```bash
sudo -i
cd /srv/pwnedhub
export COMPOSE_FILE=docker-compose.yaml:docker-compose.prod.yaml
```

## Services

| Service | Domain | Role |
|---------|--------|------|
| `proxy` | `:80` | nginx reverse proxy — routes by `Host` to the app services |
| `app` | www.pwnedhub.com | Main server-rendered app (Jinja2, session auth) |
| `sso` | sso.pwnedhub.com | OIDC/SSO provider |
| `spa` | test.pwnedhub.com | Vue SPA frontend |
| `api` | api.pwnedhub.com | REST API + WebSockets (JWT) |
| `admin` | admin.pwnedhub.com | Security-control toggles + webmail inbox |
| `api-worker` | — | RQ worker for async scans — runs the security tools |
| `bot-worker` | — | Selenium adminbot (Firefox/geckodriver) |
| `db` | — | MySQL (persistent `dbdata` volume) |
| `redis` | — | Redis (RQ queues) |

## Stack lifecycle

The stack is managed by the `docker-compose@pwnedhub` systemd unit and starts on boot:

```bash
systemctl status  docker-compose@pwnedhub
systemctl restart docker-compose@pwnedhub
systemctl stop    docker-compose@pwnedhub
systemctl start   docker-compose@pwnedhub
```

Direct compose control (e.g. to restart a single service):

```bash
docker compose ps                 # status
docker compose restart app        # restart one service
docker compose restart proxy      # after recreating an app service (nginx caches upstream IPs)
docker compose down               # stop — the dbdata/artifacts volumes PERSIST
```

## Logs

```bash
docker compose logs                     # all services
docker compose logs -f api              # follow one service
docker compose logs --tail=100 app      # last 100 lines
docker compose logs --since=10m api-worker
docker compose logs -f api-worker       # watch scans execute
docker compose logs -f bot-worker       # watch the adminbot
docker compose exec bot-worker tail -f /tmp/rq-geckodriver.log   # Firefox/geckodriver trace
```

## Inspect

```bash
docker compose ps                       # running services + ports
docker stats                            # live CPU/mem per container
docker compose images                   # image per service
docker inspect $(docker compose ps -q api)
docker network inspect pwnedhub_default # service network / aliases
docker volume ls                        # persistent volumes: pwnedhub_dbdata, pwnedhub_artifacts
```

## Shell / exec

```bash
docker compose exec app bash                                  # shell in a running container
docker compose exec api python3                               # Python REPL
docker compose exec app flask <command>                       # app CLI (init/export/purge)
```

## Databases & queues

```bash
docker compose exec db mysql -uroot -padminpass                    # MySQL shell
docker compose exec db mysql -uroot -padminpass pwnedhub           # a specific database
docker compose exec redis redis-cli                                # Redis shell
docker compose exec redis redis-cli LLEN pwnedapi-tasks            # scan queue depth
docker compose exec redis redis-cli LLEN adminbot-tasks            # adminbot queue depth
```

## Verify the security tools

```bash
docker compose exec api-worker sh -c 'dig -v; nmap --version | head -1; nikto -Version | head -1; sqlmap --version; sslyze --version'
```

## Reset / reseed

The database persists on a named volume, so reset is an explicit reseed. Baked-in helpers do it:

```bash
pwnedhub-reset        # default dataset
pwnedhub-reset-ctf    # CTF dataset
```

Each helper reseeds the three databases from `database/<dataset>/*.sql`, clears the uploaded artifacts, flushes the Redis queues, and restarts the app containers.

## Update in place

The canonical way to update is baking and launching a new AMI. To update an existing instance in place instead:

```bash
git pull                                    # /srv/pwnedhub is a clone of the repo
docker compose -f docker-compose.yaml build # rebuild the shared base image
docker compose build                        # rebuild the per-service prod images (overlay)
systemctl restart docker-compose@pwnedhub
```
