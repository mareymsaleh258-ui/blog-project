from fastapi import FastAPI, Request
from database.db import Base, engine
from routes import users, auth, posts, comments, dashboard
from core.logger import logger
import time

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Blog Management System")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"{request.method} {request.url.path} "
        f"| status: {response.status_code} "
        f"| duration: {duration}ms"
    )
    return response

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(dashboard.router)