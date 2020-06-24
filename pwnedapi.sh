# script to launch the development environment
read -p "Reset the database on load (y/n)? " -r
mysql.server start
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Resetting the database..."
    mysql -u root -padminpass pwnedhub < pwnedhub.sql
fi
read -p "Development environment with auto-reload (y/n)? " -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Running in development mode..."
    python ./pwnedapi.py
else
    echo "Running in production-like mode..."
    sudo gunicorn --bind 127.0.0.1:5002 pwnedapi.wsgi:app --error-logfile - --log-level DEBUG
fi
mysql.server stop
