from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from .. import database, models, utils, oauth2, schemas


router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    # This is the format of the user_credentials
    # username = user_credentials.username - it will accept email
    # password = user_credentials.password
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")

    # create token
    # return token

    ACCESS_TOKEN = oauth2.create_access_token(data={"user_id": str(user.id)})
    return {"access_token": ACCESS_TOKEN, "token_type": "bearer"}
