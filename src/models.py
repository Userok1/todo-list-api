from pydantic import BaseModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    

class RefreshToken(BaseModel):
    refresh_token: str
    

class RefreshTokenInDB(RefreshToken):
    sub: str
    

class Tokens(AccessToken, RefreshToken):
    pass

# User
class User(BaseModel):
    name: str
    email: str
    
    model_config = {"from_attributes": True}


class UserInDB(User):
    id: int
    password: str
    

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    

# Task
class Todo(BaseModel):
    title: str
    description: str
    

class TodoRead(Todo):
    id: int


class TodoAdd(Todo):
    user_id: int
    

class TodoInDB(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    
    model_config = {"from_attributes": True}
    

class TodosRead(BaseModel):
    todos: list[TodoRead | None] = []
    page: int = 0
    limit: int = 12
    total: int = 0