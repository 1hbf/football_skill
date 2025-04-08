from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ai import run_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "API is live"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    full_name: str = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    diet: str = Form(...),
    training: str = Form(...),
    position: str = Form(...)
):
    try:
        print("🚀 تحليل بدأ")
        temp_video_path = f"temp_{file.filename}"
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print("📁 تم حفظ الفيديو مؤقتًا")

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, lambda: run_model(
                temp_video_path,
                full_name=full_name,
                weight=weight,
                height=height,
                diet=diet,
                training=training,
                position=position
            ))
        print("✅ تم تحليل الفيديو")

        os.remove(temp_video_path)
        return JSONResponse(content={"result": result})

    except Exception as e:
        print("🔥 خطأ أثناء التحليل:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})
