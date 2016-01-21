# PwnedHub

PwnedHub is a vulnerable application designed exclusively for the [#PWAPT](http://www.lanmaster53.com/training/) training course. PwnedHub contains intentional vulnerability and should never be exposed to the open Internet. This software is NOT Open Source. See the `LICENSE.txt` file for more information.

## Installation (Ubuntu)

1. Install [pip](https://pip.pypa.io/en/stable/installing/).
2. Clone the PwnedHub repository.

    ```
    $ git clone https://LaNMaSteR53@bitbucket.org/LaNMaSteR53/pwnedhub.git
    ```

3. Install the dependencies.

    ```
    $ cd pwnedhub
    $ pip install libmysqlclient-dev
    $ pip install -r REQUIREMENTS.txt
    ```

4. Install/configure the database.
    * SQLite3
        1. Ensure that the entire PwnedHub directory tree is readable and writeable by the current user.
    * MySQL:
        1. Install MySQL.
        2. Create a database named `pwnedhub`.
        3. Edit the configuration file `pwnedhub/__init__.py`.
            1. Comment out the SQLite connection string.
            2. Uncomment the MySQL connection string.
            3. Update the MYSQL connection string with the proper credentials.
6. Initialize the database in a Python interpreter.

    ```
    $ python
    >>> import pwnedhub
    >>> pwnedhub.initdb()
    ```

7. Start the PwnedHub server.

    ```
    $ python ./pwnedhub.py
    ```

8. Visit the application and register a user.
9. Promote the user to the "administrator" role in a Python interpreter.

    ```
    $ python
    >>> import pwnedhub
    >>> pwnedhub.make_admin('username')
    ```

10. Start the server again and engage the target.

    ```
    $ python ./pwnedhub.py
    ```
