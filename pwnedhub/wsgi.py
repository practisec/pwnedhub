from pwnedhub import create_app

app, socketio = create_app('Production')
if __name__ == '__main__':
    app.run()
