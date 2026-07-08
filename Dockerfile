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
# container. Selenium Manager (bundled with Selenium 4) fetches geckodriver at
# runtime. It lives in the shared base so every container builds off one image
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

# Disable client-side SSL to match the db service (--skip-auto-generate-certs).
RUN printf '[client]\nssl=0\n' > /etc/my.cnf

# Ubuntu 22.04's stock pip (22.0.2) is too old to build mysqlclient's sdist
# metadata; upgrade it once here so every service inherits a modern pip.
RUN pip3 install --no-cache-dir --upgrade pip

WORKDIR /src
