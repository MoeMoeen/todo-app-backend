from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date, Boolean
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi import Body
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
import os
from langchain_utils import get_task_priorities

# Define the FastAPI application
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 allows any origin (you can later restrict this)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ⬇️ NEW: Use env variable first, fallback to local DB (useful when testing locally)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://todouser:securepassword@localhost/tododb"  # fallback for local dev
)

# Database configuration
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for declarative models
Base = declarative_base()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Todo(Base):
    __tablename__ = "todos"  # name of the table in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)  # add a completed field   

# Base.metadata.create_all(bind=engine)  # Create tables in the database
# # Ensure the database tables are created before running the app


# Pydantic model for Todo item
class TodoCreate(BaseModel):
    text: str
    date: date # Pydantic will auto-parse from "2025-06-21"
    completed: bool = False  # default to False, can be toggled later

class TodoRead(BaseModel):
    id: int
    text: str
    date: date
    completed: bool = False  # include completed field in the response

    class Config:
        orm_mode = True

class TodoUpdate(BaseModel):
    text: str
    date: date
    completed: bool = False  #  👈 allow toggling completion status

    class Config:
        orm_mode = True

# Pydantic model for task prioritization request
class TasksRequest(BaseModel):
    tasks: list[str]

# Endpoint to create a new to-do item
@app.post("/todos/", response_model=TodoRead)
def create_todo(todo: Annotated[TodoCreate, Body()], db: Session = Depends(get_db)):
    db_todo = Todo(text=todo.text, date=todo.date)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Endpoint to get all to-do items, ordered by date ascending
@app.get("/todos/", response_model=List[TodoRead])
def get_todos(db: Session = Depends(get_db)):
    # todos = db.query(Todo.date.asc()).all()
    todos = db.query(Todo).order_by(Todo.date.asc()).all()  # Order by date ascending
    return todos

# Endpoint to update a to-do item by ID
@app.put("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, updated: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not db_todo:
        raise HTTPException(status_code=404, detail="To-do not found")

    db_todo.text = updated.text  # type: ignore
    db_todo.date = updated.date  # type: ignore
    db_todo.completed = updated.completed # type: ignore


    db.commit()
    db.refresh(db_todo)

    return db_todo

# Endpoint to delete a to-do item by ID
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    
    if not db_todo:
        raise HTTPException(status_code=404, detail="To-do not found")
    
    db.delete(db_todo)
    db.commit()
    
    return { "message": f"To-do with ID {todo_id} deleted." }

# Endpoint to delete all to-do items
@app.delete("/todos/all")
def delete_all_todos(db: Session = Depends(get_db)):
    deleted = db.query(Todo).delete()
    db.commit()
    return { "message": f"Deleted {deleted} to-do(s)." }

# Endpoint to get task priorities using LangChain
@app.post("/todos/insights")
async def get_task_insights(request: TasksRequest):
    """
    Given a list of tasks, return a prioritized list using LangChain.
    """
    if not request.tasks:
        raise HTTPException(status_code=400, detail="Task list cannot be empty")

    # Call the utility function to get priorities
    try:
        ai_response = get_task_priorities(request.tasks)
        return {"insights": ai_response} # Return the AI-generated insights as JSON response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create the database tables
def init_db():
    Base.metadata.create_all(bind=engine)   
    # This function can be called to initialize the database

if __name__ == "__main__":
    # init_db()  # Initialize the database when this script is run directly
    print("Database initialized successfully.")