from app import app
from config import Config


if __name__ == "__main__":
    import uvicorn
    config = Config()
    backend_host = config.BACKEND_HOST
    backend_port = int(config.BACKEND_PORT)
    reload = config.RELOAD
    db_url = config.DATABASE_URL
    app.state.DATABASE_URL = config.DATABASE_URL
    app.state.SECRET_KEY = config.SECRET_KEY
    uvicorn.run("run:app", host=backend_host, port=backend_port, reload=reload)
