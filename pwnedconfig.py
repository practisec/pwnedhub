from pwnedconfig import create_app

# docker-compose run -p 5003:5003 app python ./pwnedconfig.py

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
