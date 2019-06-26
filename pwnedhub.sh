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
    python ./pwnedhub.py
else
    echo "Running in production mode..."
    sudo gunicorn --bind 0.0.0.0:80 pwnedhub.wsgi:app
fi
mysql.server stop
