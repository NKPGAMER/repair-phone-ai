import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from typing import Optional, List
import uvicorn

# Khởi tạo FastAPI app
app = FastAPI(
    title="Phone Repair AI API",
    description="API để chẩn đoán và hỗ trợ sửa chữa điện thoại",
    version="1.0.0"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model cho request
class AnalyzeRequest(BaseModel):
    panic_log: str
    
class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

# Khởi tạo Gemini
def initialize_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY không được tìm thấy trong biến môi trường")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

# System prompt cho phone repair
SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên nghiệp về sửa chữa điện thoại di động. 

Nhiệm vụ của bạn:
1. Phân tích panic log, crash log, logcat để tìm nguyên nhân lỗi
2. Chẩn đoán các vấn đề về phần cứng và phần mềm của điện thoại
3. Hướng dẫn chi tiết cách khắc phục sự cố
4. Tư vấn về linh kiện thay thế và giá cả ước tính
5. Cung cấp các mẹo bảo dưỡng và chăm sóc điện thoại
6. Giải thích các vấn đề kỹ thuật một cách dễ hiểu

Nguyên tắc:
- Phân tích kỹ lưỡng log để tìm lỗi chính xác
- Giải thích các mã lỗi, exception, stack trace một cách rõ ràng
- Đưa ra giải pháp từ đơn giản đến phức tạp
- Cảnh báo rõ ràng về rủi ro khi tự sửa chữa
- Khuyên người dùng đến trung tâm bảo hành nếu cần thiết
- Trả lời bằng tiếng Việt một cách thân thiện và chuyên nghiệp

Khi phân tích log, hãy chú ý:
- Exception và Error messages
- Stack traces
- Memory leaks
- Kernel panic
- Hardware failures
- App crashes
"""

# Global model instance
model = None

@app.on_event("startup")
async def startup_event():
    global model
    try:
        model = initialize_gemini()
        print("✅ Gemini API initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Gemini: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Phone Repair AI API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Phân tích panic log/crash log",
            "/chat": "POST - Chat với AI assistant",
            "/health": "GET - Kiểm tra trạng thái API"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "gemini_initialized": model is not None
    }

@app.post("/analyze")
async def analyze_phone_issue(request: AnalyzeRequest):
    """
    Phân tích panic log, crash log, logcat để chẩn đoán vấn đề điện thoại
    """
    if not model:
        raise HTTPException(status_code=503, detail="Gemini API chưa được khởi tạo")
    
    if not request.panic_log or not request.panic_log.strip():
        raise HTTPException(status_code=400, detail="panic_log không được để trống")
    
    try:
        # Tạo prompt đầy đủ
        full_prompt = f"""{SYSTEM_PROMPT}

Người dùng gửi thông tin sau để chẩn đoán:

{request.panic_log}

Hãy phân tích kỹ lưỡng và đưa ra:
1. Nguyên nhân chính xác của vấn đề
2. Mức độ nghiêm trọng
3. Giải pháp khắc phục chi tiết
4. Lời khuyên phòng ngừa"""

        # Gọi Gemini API
        response = model.generate_content(full_prompt)
        
        return {
            "status": "success",
            "analysis": response.text,
            "input_length": len(request.panic_log)
        }
        
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi phân tích: {str(e)}")

@app.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    """
    Chat trực tiếp với AI assistant về sửa chữa điện thoại
    """
    if not model:
        raise HTTPException(status_code=503, detail="Gemini API chưa được khởi tạo")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="message không được để trống")
    
    try:
        # Xây dựng context với lịch sử
        context_parts = [SYSTEM_PROMPT, "\n\nCuộc trò chuyện:"]
        
        # Thêm lịch sử chat (tối đa 10 tin nhắn gần nhất)
        for msg in request.history[-10:]:
            role = "Người dùng" if msg.get("role") == "user" else "Trợ lý"
            context_parts.append(f"{role}: {msg.get('content', '')}")
        
        # Thêm tin nhắn hiện tại
        context_parts.append(f"Người dùng: {request.message}")
        
        full_context = "\n".join(context_parts)
        
        # Gọi Gemini API
        response = model.generate_content(full_context)
        
        return {
            "status": "success",
            "response": response.text,
            "message": request.message
        }
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi khi chat: {str(e)}")

# Để chạy local
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)