# Shared base image for all pwnedhub app services.
#
# Extends the stock Ubuntu release (kept close to the AWS EC2 Ubuntu AMI) with
# the common OS + Python layer: system libraries, Python, an upgraded pip, and
# the MySQL client. Application Python dependencies are NOT baked here — each
# service installs its own REQUIREMENTS.txt at container start (see the
# `command:` blocks in docker-compose.yaml), so per-service dependency sets stay
# separate and the source stays hot-mounted at /src.
#
# To rehearse the next Ubuntu LTS, bump the tag below and rebuild:
#   docker compose build
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# python3 is Python 3.10 on jammy. build-essential + python3-dev + libmariadb-dev
# + pkg-config are needed to compile mysqlclient. The client lib is libmariadb
# (MariaDB's Connector/C), NOT Oracle's libmysqlclient — MariaDB's connector
# auto-fetches the server public key, so caching_sha2_password auth works against
# the mysql server over a non-TLS connection; Oracle's client rejects it.
#
# Firefox (used only by the adminbot service) comes from Mozilla's deb repo,
# because jammy's apt `firefox` package is a snap that will not run in a
# container. It lives in the shared base so every container builds off one image
# and nothing installs packages at container start.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip build-essential python3-dev libmariadb-dev pkg-config \
        wget ca-certificates && \
    install -d -m 0755 /etc/apt/keyrings && \
    wget -qO /etc/apt/keyrings/packages.mozilla.org.asc https://packages.mozilla.org/apt/repo-signing-key.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" > /etc/apt/sources.list.d/mozilla.list && \
    printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' > /etc/apt/preferences.d/mozilla && \
    apt-get update && \
    apt-get install -y --no-install-recommends firefox && \
    rm -rf /var/lib/apt/lists/*

# geckodriver (Firefox WebDriver, adminbot only). Baked in rather than fetched by
# Selenium Manager at runtime: Selenium ships no Selenium Manager binary for
# linux/aarch64, so on ARM hosts the runtime locator can't run at all. adminbot
# points FirefoxService at /usr/bin/geckodriver, which skips Selenium Manager
# entirely. Arch is detected so the image still builds on x86_64.
RUN GECKO_VERSION=v0.37.0 && \
    case "$(dpkg --print-architecture)" in \
        arm64) GECKO_ARCH=linux-aarch64 ;; \
        amd64) GECKO_ARCH=linux64 ;; \
        *) echo "unsupported arch: $(dpkg --print-architecture)" >&2; exit 1 ;; \
    esac && \
    wget -qO /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-${GECKO_ARCH}.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/bin && \
    chmod +x /usr/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Disable client-side SSL to match the db service (--skip-auto-generate-certs).
RUN printf '[client]\nssl=0\n' > /etc/my.cnf

# Ubuntu 22.04's stock pip (22.0.2) is too old to build mysqlclient's sdist
# metadata; upgrade it once here so every service inherits a modern pip.
RUN pip3 install --no-cache-dir --upgrade pip

WORKDIR /src
