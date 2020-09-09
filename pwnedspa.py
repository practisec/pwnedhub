from pwnedspa import create_app

# docker-compose run -p 5001:5001 app python ./pwnedspa.py

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
