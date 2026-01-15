from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated, Any
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .utils import add_todo, get_todo, edit_todo, remove_todo, get_todos
from .models import UserInDB, Todo, TodoInDB, TodoAdd, TodosRead, TodoRead
from .dependencies import get_current_user
from .database import get_db
from .orm_models import TodoModel

router = APIRouter(prefix="/todos")


@router.post("/", response_model=TodoInDB, status_code=201)
async def create_todo(
    todo: Todo, 
    user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TodoInDB | None:
    todo_add = TodoAdd(**todo.model_dump(), user_id=user.id)
    todo_from_db = await add_todo(todo_add, db)
    res =  TodoInDB.model_validate(todo_from_db)
    del res.user_id
    return res

    
@router.put("/{todo_id}", response_model=TodoInDB)
async def update_todo(
    todo_id: int, 
    new_todo: Todo, 
    user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> TodoInDB | None:
    old_todo = await get_todo(todo_id, db)
    if not old_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    if old_todo.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden action",
        )
    updated_todo: TodoModel | None = await edit_todo(todo_id, new_todo, db)
    res = TodoInDB.model_validate(updated_todo)
    del res.user_id
    return res


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
) -> None:
    todo: TodoModel | None = await get_todo(todo_id, db)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    if todo.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden action",
        )

    await remove_todo(todo_id, db)
    

@router.get("/", response_model=TodosRead)
async def read_todos(
    user: Annotated[UserInDB, Depends(get_current_user)],
    db: Annotated[async_sessionmaker[AsyncSession], Depends(get_db)],
    page: Annotated[int, Query(gt=0)] = 1,
    limit: Annotated[int, Query(gt=0)] = 12,
) -> Any:
    todos: list[TodoModel] | None = await get_todos(db, page, limit)
    if not todos:
        return TodosRead(todos=[], page=page, limit=limit, total=0)
    
    if not all((todo.user_id == user.id for todo in todos)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden action",
        )
    todos_without_user_id = []
    for todo in todos:
        todo = TodoInDB.model_validate(todo)
        del todo.user_id
        todos_without_user_id.append(TodoRead(**todo.model_dump()))
    res = TodosRead(todos=todos_without_user_id, page=page, limit=limit, total=len(todos_without_user_id))
    return res
