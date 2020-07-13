from pwnedapi import create_app
import os

app, socketio = create_app(os.environ.get('CONFIG', 'Production'))
if __name__ == '__main__':
    app.run()
