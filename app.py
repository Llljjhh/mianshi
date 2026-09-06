from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
import json

app = FastAPI()

#允许Gitee Pages前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_URL = "https://api.dify.ai/v1/chat-messages"

#健康检测接口，用来防休眠
@app.get("/health")
async def health():
    return {"status":"ok"}

@app.post("/api/chat")
async def chat(question:str):
    headers = {"Authorization":f"Bearer {DIFY_API_KEY}","Content-Type":"application/json"}
    payload={
        "inputs":{},
        "query":question,
        "response_mode":"streaming",
        "user":"web_user"
    }
    async def stream():
        async with httpx.AsyncClient() as client:
            async with client.stream("POST",DIFY_URL,headers=headers,json=payload,timeout=120) as resp:
                async for chunk in resp.aiter_bytes():
                    yield chunk
    return StreamingResponse(stream(),media_type="text/event-stream")
