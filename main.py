from fastapi import FastAPI, Depends, status, Response, HTTPException
import schemas,models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a blog
@app.post("/blog", status_code=status.HTTP_201_CREATED, tags=["blogs"])
def create_blog(blog: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=blog.title, body=blog.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

# Get all blogs
@app.get('/blog', response_model = List[schemas.ShowBlog], tags=["blogs"])
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

# Get a blog by ID
@app.get('/blog/{id}', status_code=200,response_model = schemas.ShowBlog, tags=["blogs"])
def show(id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with the id {id} is not available"
        )
        #response.status_code = status.HTTP_404_NOT_FOUND
        #return {'detail': f"Blog with the id {id} is not available"}
    return blog

# Delete a Blog
@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT, tags=["blogs"])
def destroy(id: int, db: Session = Depends(get_db)):
    logging.warning(f"Trying to delete blog with id: {id}")
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        logging.warning("Blog not found.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Blog with id {id} not found")
    db.delete(blog)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update the Blog
@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED, tags=["blogs"])
def update(id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found")

    blog.update(request.dict())
    # dict() is used to convert a Pydantic model to a regular Python dictionary so that SQLAlchemy can use it for the update operation.
    db.commit()
    return {'message': 'Updated'}
