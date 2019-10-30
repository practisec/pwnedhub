# PwnedHub

PwnedHub is a vulnerable application designed exclusively for the [PWAPT](http://www.lanmaster53.com/training/) training course. PwnedHub contains intentional vulnerability and should never be exposed to the open Internet. This software is NOT Open Source. See the `LICENSE.txt` file for more information.

## Using Docker

1. Install Docker Desktop.
2. Clone the PwnedHub repository.

    ```
    $ git clone https://github.com/lanmaster53/pwnedhub.git
    ```

3. Change into the PwnedHub directory.

    ```
    $ cd pwnedhub
    ```

4. Build the PwnedHub Docker image.

    ```
    docker build --rm -t pwnedhub .
    ```

5. Launch the PwnedHub architecture using Docker Compose.

    ```
    docker-compose up
    ```

    * To launch as a daemon (no terminal logging), add the `-d` switch.

6. When done using PwnedHub, clean up the Docker environment with the following command:

    ```
    docker-compose down
    ```

## Installation (Ubuntu)

1. Install [pip](https://pip.pypa.io/en/stable/installing/).
2. Clone the PwnedHub repository.

    ```
    $ git clone https://github.com/lanmaster53/pwnedhub.git
    ```

3. Install the dependencies. I recommend using `virtualenv` to keep things tidy. The below commands **do not** implement `virtualenv` and will install to your global pip environment.

    ```
    $ cd pwnedhub
    $ pip install -r REQUIREMENTS.txt
    ```

    Note: In Ubuntu, the `lxml` dependency may require installing the `python-dev`, `libxml2-dev`, `libxslt-dev`, and `lib32z1-dev` packages. Look for errors during the above process and install the needed packages. Systems other than Ubuntu will likely also require some sort of finagling to get to work. MacOS worked without issue.

4. Install and configure MySQL.
    * Set the MySQL `root` user password to `adminpass`
5. Initialize the database.

    ```
    $ mysql -u root -p -e "CREATE DATABASE pwnedhub"
    $ mysql -u root -p pwnedhub < pwnedhub.sql
    ```

6. Add the application's database user.

    ```
    $ mysql -h localhost -u root -padminpass
    > CREATE USER 'pwnedhub'@'localhost' IDENTIFIED BY 'dbconnectpass';
    > GRANT ALL PRIVILEGES ON pwnedhub.* TO 'pwnedhub'@'localhost';
    > FLUSH PRIVILEGES;
    > SHOW GRANTS FOR 'pwnedhub'@'localhost';
    > exit;
    ```

7. Modify the hosts file to create the following records:

    ```
    127.0.0.1   pwnedhub.com
    127.0.0.1   api.pwnedhub.com
    ```

8. Start the MySQL server.

    ```
    $ sudo systemctl start mysql
    ```

9. Start the PwnedHub application.

    ```
    $ python ./pwnedhub.py
    ```

10. Start the PwnedAPI application.

    ```
    $ python ./pwnedapi.py
    ```

11. Visit the application at http://pwnedhub.com:5000.
