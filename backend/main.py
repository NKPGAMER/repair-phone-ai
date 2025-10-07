from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

# --- Cấu hình Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# Cho phép mọi domain gọi (có thể thay * bằng domain GitHub Pages của Phúc)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogRequest(BaseModel):
    panic_log: str

@app.get("/")
def root():
    return {"message": "AI Backend đang hoạt động."}

@app.get("/ping")
def ping():
    return {"status": "alive"}

@app.post("/analyze")
def analyze_log(req: LogRequest):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    Bạn là kỹ thuật viên chuyên sửa iPhone.
    Đây là panic log cần phân tích:
    {req.panic_log}

    Hãy xác định khả năng phần cứng hoặc phần mềm bị lỗi 
    và gợi ý kiểm tra hoặc hướng khắc phục cụ thể.
    """

    try:
        response = model.generate_content(prompt)
        return {"answer": response.text}
    except Exception as e:
        return {"answer": f"Lỗi khi gọi Gemini API: {str(e)}"}
