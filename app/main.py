from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import chat
from app.router import user
from app.router import upload_file
from app.router import chat_history
from app.router import technical_error
import uvicorn

app = FastAPI(
)

app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],  # hoặc chỉ định domain cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(user.router)
app.include_router(upload_file.router)
app.include_router(chat_history.router)
app.include_router(technical_error.router)

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000) 
