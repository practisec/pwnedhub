from pwnedapi import create_app

app = create_app('Production')
if __name__ == '__main__':
    app.run()
