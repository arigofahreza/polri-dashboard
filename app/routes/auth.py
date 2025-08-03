from fastapi import APIRouter, HTTPException
from app.schemas.user import UserLogin, UserOut
from app.crud.user import get_user_by_credentials

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post("/login", response_model=UserOut)
async def login(user: UserLogin):
    db_user = await get_user_by_credentials(user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return db_user
