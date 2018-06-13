# PwnedHub

PwnedHub is a vulnerable application designed exclusively for the [PWAPT](http://www.lanmaster53.com/training/) training course. PwnedHub contains intentional vulnerability and should never be exposed to the open Internet. This software is NOT Open Source. See the `LICENSE.txt` file for more information.

## Installation (Ubuntu)

1. Install [pip](https://pip.pypa.io/en/stable/installing/).
2. Clone the PwnedHub repository.

    ```
    $ git clone https://github.com/lanmaster53/pwnedhub.git
    ```

3. Install the dependencies. I recommend using `virtualenv` to keep things tidy. The below commands **do not** implement `virtualenv`.

    ```
    $ cd pwnedhub
    $ pip install -r REQUIREMENTS.dev.txt
    ```

    Note: In Ubuntu, the `lxml` dependency may require installing the `python-dev`, `libxml2-dev`, `libxslt-dev`, and `lib32z1-dev` packages. Look for errors during the above process and install the needed packages. Systems other than Ubuntu will likely also require some sort of finagling to get to work. MacOS worked without issue.

4. Install/configure the database (SQLite3).
    * Ensure that the entire PwnedHub directory tree is readable and writeable by the current user. This should already be the case if the current user cloned the repository.
6. Initialize the database in a Python interpreter.

    ```
    $ python
    >>> import pwnedhub
    >>> pwnedhub.init_db()
    ```

7. Start the PwnedHub server.

    ```
    $ python ./pwnedhub.py
    ```

8. Visit the application and register a user.

Administrative access can be gained through exploiting the application. However, to create an administrative user, promote a previously created user to the "administrator" role in a Python interpreter.

    ```
    $ python
    >>> import pwnedhub
    >>> pwnedhub.make_admin('username')
    ```
