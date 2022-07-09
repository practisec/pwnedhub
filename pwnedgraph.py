from pwnedgraph import create_app

# docker-compose run -p 5004:5004 app python ./pwnedgraph.py

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
