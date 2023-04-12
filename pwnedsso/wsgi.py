from pwnedsso import create_app
import os

app = create_app(os.environ.get('CONFIG', 'Production'))
if __name__ == '__main__':
    app.run()
