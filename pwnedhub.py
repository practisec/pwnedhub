from pwnedhub import create_app

# docker-compose run -p 5000:5000 app python ./pwnedhub.py

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
