import os
import uvicorn

if os.getenv('API_ENV') != 'production':
    from dotenv import load_dotenv

    load_dotenv()

from fastapi import FastAPI
from routers import webhooks

app = FastAPI()

app.include_router(webhooks.router)

@app.get('/')
def index():
    return {"message": "Hello World"}


if __name__ == "__main__":
    reload = True if os.getenv('API_ENV') != 'production' else False
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=reload)