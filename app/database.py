from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

# SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<hostname>/<database_name>"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{
    settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# don't do this put variables in .env or config.ini

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This was implemented to make sure database is connected before running the code
# Thsi works for minor issues like internet connection etc
# while True:
#     try:
#         connection = psycopg2.connect(
#             host='localhost', database='fastapi', user='postgres', password='boywithuke',
#             port="5432", cursor_factory=RealDictCursor)
#         if connection:
#             print(connection.info)
#         cursor = connection.cursor()
#         print("Database connected")
#         break
#     except Exception as e:
#         print(e)
#         print("Database to database failed")
#         time.sleep(1.5)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
