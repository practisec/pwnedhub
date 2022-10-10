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
    127.0.0.1   test.pwnedhub.com
    127.0.0.1   api.pwnedhub.com
    127.0.0.1   graph.pwnedhub.com
    127.0.0.1   config.pwnedhub.com
    ```

7. Visit the various applications and API interfaces:
    * http://www.pwnedhub.com
    * http://test.pwnedhub.com
    * http://api.pwnedhub.com/swaggerui/index.html
    * http://graph.pwnedhub.com/graphql
    * http://graph.pwnedhub.com/voyager
    * Postman collection files for the REST and GraphQL APIs are available in the Github repository under the "resources" folder.
8. When done using PwnedHub, clean up the Docker environment with the following command:

    ```
    docker compose down
    ```

## Development Usage

The repository includes launch scripts for each part of the application. The scripts still use Docker, but run each service on a development server without a reverse proxy. This allows for auto-reloading and interactive debugging.

1. Conduct steps 1-4 and 6 above.
2. Start the PwnedHub legacy application.

    ```
    $ docker compose run -p 5000:5000 app python ./pwnedhub.py
    ```

3. Open a new tab and start the PwnedHub 2.0 application.

    ```
    $ docker compose run -p 5001:5001 app python ./pwnedspa.py
    ```

4. Open a new tab and start the PwnedHub API.

    ```
    $ docker compose run -p 5002:5002 app python ./pwnedapi.py
    ```

5. Open a new tab and start the PwnedHub GraphQL API.

    ```
    $ docker compose run -p 5004:5004 app python ./pwnedgraph.py
    ```

6. Open a new tab and start the PwnedConfig application.

    ```
    $ docker compose run -p 5003:5003 app python ./pwnedconfig.py
    ```

7. Visit the various applications and API interfaces:
    * http://www.pwnedhub.com:5000
    * http://test.pwnedhub.com:5001
    * http://api.pwnedhub.com:5002/swaggerui/index.html
    * http://graph.pwnedhub.com:5004/graphql
    * http://graph.pwnedhub.com:5004/voyager
    * Postman collection files for the REST and GraphQL APIs are available in the Github repository under the "resources" folder.
8. When done using PwnedHub, close all tabs and clean up the Docker environment with the following command:

    ```
    docker compose down
    ```
