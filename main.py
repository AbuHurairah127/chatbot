from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent import generate_reply
from database import UserModel, get_db, init_db

app = FastAPI(title="Chatbot Users API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    name: str
    email: str
    age: int


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class PromptResponse(BaseModel):
    prompt: str
    reply: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"message": "Users API is running. Use /users to list or create users."}


@app.get("/users", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(UserModel).order_by(UserModel.id).all()


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users", response_model=User, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserModel(name=payload.name, email=payload.email, age=payload.age)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/chat", response_model=PromptResponse)
def chat(payload: PromptRequest):
    prompt = payload.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        reply = generate_reply(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq agent failed: {exc}") from exc

    return PromptResponse(prompt=prompt, reply=reply)
