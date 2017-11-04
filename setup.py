from setuptools import setup, find_packages
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

with open(path.join(here, 'LICENSE.txt')) as f:
    license = f.read()

setup(
    name='PwnedHub',
    version='1.0',
    description='',
    long_description=long_description,
    author='Tim Tomes (lanmaster53)',
    author_email='tim.tomes@practicalsecurity.services',
    license=license,
    url='https://www.lanmaster53.com/training/',
    packages=find_packages(),
    include_package_data=True,
    data_files=[],
    entry_points={
        'console_scripts': [
            'pwnedhub = pwnedhub.pwnedhub:start',
            'pwnedhub_init_db = pwnedhub.pwnedhub:init_db',
            'pwnedhub_make_admin = pwnedhub.pwnedhub:make_admin'
        ]
    },
    install_requires=[
        'Flask==0.10.1',
        'Flask-MySQLdb==0.2.0',
        'Flask-Spyne==0.2',
        'Flask-SQLAlchemy==2.0',
        'gunicorn==19.3.0',
        'itsdangerous==0.24',
        'Jinja2==2.8',
        'lxml==3.4.4',
        'MarkupSafe==0.23',
        'mysqlclient==1.3.6',
        'pytz==2015.7',
        'PyYAML==3.11',
        'sec-wall==1.2',
        'spyne==2.12.10',
        'SQLAlchemy==1.0.8',
        'Werkzeug==0.10.4',
        'wheel==0.24.0'
    ])
