<img src="/common/static/images/logo-filled.png" style="width: 50%" />

PwnedHub is a vulnerable application designed exclusively for [PractiSec training courses](https://www.practisec.com/training/). PwnedHub contains intentional vulnerability and should never be exposed to the open Internet. This software is NOT Open Source in a traditional sense. See the `LICENSE.txt` file for more information.

## Requirements

* Docker

## Installation and Usage

1. Install Docker Desktop.
2. Clone the PwnedHub repository.

    ```
    $ git clone https://github.com/lanmaster53/pwnedhub.git
    ```

3. Change into the PwnedHub directory.

    ```
    $ cd pwnedhub
    ```

4. Build the PwnedHub Docker images.

    ```
    docker compose build
    ```

5. Launch the PwnedHub environment using Docker Compose.

    ```
    docker compose up
    ```

    * To launch as a daemon (no terminal logging), add the `-d` switch.

6. Modify the hosts file to create the following records:

    ```
    127.0.0.1   www.pwnedhub.com
    127.0.0.1   sso.pwnedhub.com
    127.0.0.1   test.pwnedhub.com
    127.0.0.1   api.pwnedhub.com
    127.0.0.1   admin.pwnedhub.com
    ```

7. Visit the various target applications:
    * http://www.pwnedhub.com
    * http://test.pwnedhub.com
    * http://api.pwnedhub.com
    * http://sso.pwnedhub.com
8. When done using PwnedHub, shut down the Docker environment with the following command:

    ```
    docker compose down
    ```

## Information

The PwnedHub environment includes several resources that are not targets.

1. http://admin.pwnedhub.com/inbox/ - A webmail interface for receiving email from out-of-band systems. PwnedHub does not send email to external mail services, so when an application sends an email, this is where the user will receive it.
2. http://admin.pwnedhub.com/config/ - A configuration interface for enabling/disabling security controls and features. Modifying these settings change how the target applications behave.

Postman collection files for the REST API are available in the "resources" folder.
