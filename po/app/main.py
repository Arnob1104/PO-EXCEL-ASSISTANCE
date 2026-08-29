from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import chat, po

app = FastAPI(title="PO Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://po-excel-assistance.vercel.app/"],  # tighten this to your frontend domain(s) before launch
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(po.router)


@app.get("/health")
def health():
    return {"status": "ok"}
