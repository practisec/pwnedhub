from pwnedfast import create_app
import os

# uvicorn pwnedfast.asgi:app --reload

app = create_app()#os.environ.get('CONFIG', 'Production'))
