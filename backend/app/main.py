from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chatbot, excel, health, news, schedules

app = FastAPI(title="공공직군 행정업무 슈퍼앱 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(schedules.router, prefix="/api")
app.include_router(excel.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(news.router, prefix="/api")
