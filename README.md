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

5. Launch the PwnedHub architecture using Docker Compose.

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
    127.0.0.1   config.pwnedhub.com
    ```

7. Visit the various applications and API interfaces:
    * http://www.pwnedhub.com
    * http://test.pwnedhub.com
    * http://api.pwnedhub.com/swaggerui/index.html
    * Postman collection files for the REST API are available in the Github repository under the "resources" folder.
8. When done using PwnedHub, clean up the Docker environment with the following command:

    ```
    docker compose down
    ```
