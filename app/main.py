from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routers import posts, users, auth, votes
from .config import settings


# sqlalchemy 1.4 can't be used to make changes to table schemas
# To do that you havet use alembic
app = FastAPI()

# if you want your api to only be communicated by a web app your provide just the web app
origins = ["*"]

# To allow everyone to access your api using cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(votes.router)

models.Base.metadata.create_all(bind=engine)

# requests Get method url: "/"


@app.get("/")
def root():
    return {"message": 'Hello World'}
