from fastapi import APIRouter
from app.entities.models import User
from app.config.auth import register_user, login_user

router = APIRouter()

@router.post("/register")
def register(user: User):
    uid = register_user(user.username, user.password)
    return {"user_id": uid} if uid else {"error": "Username đã tồn tại"}

@router.post("/login")
def login(user: User):
    uid = login_user(user.username, user.password)
    return {"user_id": uid} if uid else {"error": "Sai tài khoản hoặc mật khẩu"}
