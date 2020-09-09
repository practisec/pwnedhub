from pwnedapi import create_app

# docker-compose run -p 5002:5002 app python ./pwnedapi.py

app, socketio = create_app()
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5002)
