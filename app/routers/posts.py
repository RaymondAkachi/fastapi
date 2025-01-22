from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, oauth2, schemas, utils
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional


router = APIRouter(
    prefix="/posts",
    tags=['posts']
)

# @router.get("/", response_model=List[schemas.PostOut])

# @router.get("/", response_model=List[schemas.PostOut])


@router.get("/")
def get_posts(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user), limit: int = 10,
              skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts;""")
    # posts = cursor.fetchall()

    # Offet is used to skip a specified number of the first entries shown
    # contaisn is used to check if the search is somewhere in the title of the ost

    # posts = db.query(models.Post).filter(
    #     models.Post.title.contains(search)).limit(limit).offset(skip).all()

    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    user_out = db.query(
        models.Post.id,
        models.Post.owner_id,
        models.User.email,
        models.Post.created_at
    ).join(models.User, models.Post.owner_id == models.User.id, isouter=True).group_by(models.Post.id, models.Post.owner_id, models.User.email, models.Post.created_at).all()
    response = []

    for post, votes in posts:
        # Convert the SQLAlchemy model to a dict
        post_dict = jsonable_encoder(post)
        post_dict["votes"] = votes
        post_dict["owner"] = {}
        for i in user_out:
            if i[0] == post.id:
                post_dict['owner']["id"] = i[1]
                post_dict['owner']["email"] = i[2]
                post_dict['owner']["created_at"] = i[3]
        response.append(post_dict)

    return response
    # return results


@router.post("/", response_model=schemas.Output)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
    #                (post.title, post.content, post.published))

    # new_post = cursor.fetchone()

    # connection.commit()
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    new_post = models.Post(  # Does the same thing as the code above
        owner_id=current_user.id, **post.model_dump()
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# We chose to let a user that is not logged in to see the latest post


@router.get("/latest", response_model=schemas.Output)
def get_latest_post(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * from posts ORDER BY id DESC LIMIT 1""")
    # latest_post = cursor.fetchone()
    # return {"data": latest_post}
    post = db.query(models.Post).order_by(models.Post.id.desc()).first()

    return post


@router.get("/my_posts",  response_model=List[schemas.Output])
def get_post(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).filter(
        models.Post.owner_id == current_user.id).all()

    return posts

# @router.get("/{id}", response_model=schemas.PostOut)


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    # cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # post = cursor.fetchone()
    # if not post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Post with id: {id} not found")

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found")

    user_out = db.query(
        models.Post.id,
        models.Post.owner_id,
        models.User.email,
        models.Post.created_at
    ).join(models.User, models.Post.owner_id == models.User.id, isouter=True).filter(models.Post.id == id).group_by(models.Post.id, models.Post.owner_id, models.User.email, models.Post.created_at).first()

    post_dict = {
        "id": post[0].id,
        "title": post[0].title,  # Replace 'title' with actual column name
        # Replace 'content' with actual column name
        "content": post[0].content,
        # Replace 'owner_id' with actual column name
        "owner_id": post[0].owner_id,
        # Replace with any other column you want
        "created_at": post[0].created_at,
        "votes": post[1],  # Count of votes
    }

    post_dict["owner"] = {
        "id": user_out[1],
        "email": user_out[2],
        "created_at": user_out[3]
    }

    return post_dict


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,  db: Session = Depends(get_db), current_user: str = Depends(oauth2.get_current_user)):
    # cursor.execute("DELETE FROM posts WHERE id=%s RETURNING *", (str(id),))
    # deleted_post = cursor.fetchone()
    # connection.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    print(post.owner_id)
    print(current_user.id)
    if int(post.owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    print("Post deleted")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Output)
def update_post(id: int, new_values: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(f"UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
    #                (post.title, post.content, post.published, str(id)))
    # match = cursor.fetchone()
    # connection.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    # Have not tries removing the integer converters if you are free you can find out
    if int(post.owner_id) != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.update(new_values.model_dump(), synchronize_session=False)

    db.commit()

    # Fetching new_post with the id entered to the user
    return post_query.first()
