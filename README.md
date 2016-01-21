# PwnedHub

PwnedHub is the target application for the [#PWAPT](http://www.lanmaster53.com/training/) training course. PwnedHub contains intentional vulnerability and should never be exposed to the open Internet. Use at your own risk.

## Installation

* Download the repository.

```
$ git clone https://github.com/lanmaster53/PwnedHub.git
```

* Install the dependencies.

```
$ cd PwnedHub
$ pip install -r REQUIREMENTS.txt
```

* Ensure that the entire PwnedHub directory is readable and writeable by the current user.
* Initialize the database in a Python interpreter.

```
$ python
>>> import pwnedhub
>>> pwnedhub.initdb()
```

* Start the PwnedHub server.

```
$ python ./pwnedhub.py
```

* Visit the application and register a user.
* Promote the user to the "administrator" role in a Python interpreter.

```
$ python
>>> import pwnedhub
>>> pwnedhub.make_admin('username')
```

* Start the server again and engage the target.

```
$ python ./pwnedhub.py
```
