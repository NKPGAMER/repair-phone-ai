from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os

# Cấu hình API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Khởi tạo model (chuẩn mới)
model = genai.GenerativeModel(model_name="gemini-2.0-pro")

app = FastAPI()

# Cho phép frontend truy cập (CORS)
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

@app.post("/analyze")
def analyze_log(req: LogRequest):
    try:
        # prompt = f"Phân tích log sau và gợi ý hướng sửa chữa iPhone:\n\n{req.panic_log}"
        # response = model.generate_content(prompt)
        return {"answer": os.getenv("GEMINI_API_KEY")}
    except Exception as e:
        return {"error": f"Lỗi khi gọi Gemini API: {e}"}
