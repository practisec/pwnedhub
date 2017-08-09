from pwnedhub import create_app

if __name__ == '__main__':
    app = create_app('Production')
    app.run()
