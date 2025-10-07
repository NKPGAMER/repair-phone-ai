import os
import google.generativeai as genai
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class ChatMessage:
    """Lớp đại diện cho một tin nhắn trong cuộc trò chuyện"""
    role: str  # 'user' hoặc 'model'
    content: str

class PhoneRepairAssistant:
    """
    Backend để hỗ trợ sửa chữa điện thoại sử dụng Gemini API
    """
    
    def __init__(self):
        """Khởi tạo kết nối với Gemini API"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY không được tìm thấy trong biến môi trường")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat_history: List[ChatMessage] = []
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self) -> str:
        """Tạo system prompt để huấn luyện mô hình"""
        return """Bạn là trợ lý AI chuyên nghiệp về sửa chữa điện thoại di động. 
        
Nhiệm vụ của bạn:
1. Chẩn đoán các vấn đề về phần cứng và phần mềm của điện thoại
2. Hướng dẫn chi tiết cách khắc phục sự cố
3. Tư vấn về linh kiện thay thế và giá cả ước tính
4. Cung cấp các mẹo bảo dưỡng và chăm sóc điện thoại
5. Giải thích các vấn đề kỹ thuật một cách dễ hiểu

Nguyên tắc:
- Luôn hỏi thông tin cụ thể về triệu chứng trước khi chẩn đoán
- Đưa ra giải pháp từ đơn giản đến phức tạp
- Cảnh báo rõ ràng về rủi ro khi tự sửa chữa
- Khuyên người dùng đến trung tâm bảo hành nếu cần thiết
- Trả lời bằng tiếng Việt một cách thân thiện và chuyên nghiệp"""

    def send_message(self, user_message: str) -> str:
        """
        Gửi tin nhắn và nhận phản hồi từ Gemini
        
        Args:
            user_message: Tin nhắn từ người dùng
            
        Returns:
            Phản hồi từ mô hình Gemini
        """
        try:
            # Thêm tin nhắn người dùng vào lịch sử
            self.chat_history.append(ChatMessage(role="user", content=user_message))
            
            # Tạo context với system prompt và lịch sử chat
            full_context = self._build_context()
            
            # Gửi yêu cầu đến Gemini
            response = self.model.generate_content(full_context)
            
            # Lấy phản hồi
            bot_response = response.text
            
            # Lưu phản hồi vào lịch sử
            self.chat_history.append(ChatMessage(role="model", content=bot_response))
            
            return bot_response
            
        except Exception as e:
            error_msg = f"Lỗi khi gọi Gemini API: {str(e)}"
            print(error_msg)
            return "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau."
    
    def _build_context(self) -> str:
        """Xây dựng context đầy đủ cho mô hình"""
        context_parts = [self.system_prompt, "\n\nLịch sử trò chuyện:"]
        
        # Chỉ lấy 10 tin nhắn gần nhất để tránh vượt quá giới hạn token
        recent_history = self.chat_history[-10:]
        
        for msg in recent_history:
            prefix = "Người dùng" if msg.role == "user" else "Trợ lý"
            context_parts.append(f"{prefix}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def reset_conversation(self):
        """Đặt lại cuộc trò chuyện"""
        self.chat_history = []
        print("Đã đặt lại cuộc trò chuyện")
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """Lấy lịch sử trò chuyện"""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.chat_history
        ]
    
    def export_chat_history(self, filepath: str):
        """Xuất lịch sử trò chuyện ra file JSON"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.get_chat_history(), f, ensure_ascii=False, indent=2)
            print(f"Đã xuất lịch sử trò chuyện ra {filepath}")
        except Exception as e:
            print(f"Lỗi khi xuất file: {str(e)}")


# Hàm tiện ích để sử dụng trực tiếp
def create_assistant() -> PhoneRepairAssistant:
    """Tạo instance của PhoneRepairAssistant"""
    return PhoneRepairAssistant()


# Ví dụ sử dụng
if __name__ == "__main__":
    # Khởi tạo assistant
    assistant = create_assistant()
    
    print("=== Trợ lý sửa chữa điện thoại ===")
    print("Gõ 'exit' để thoát, 'reset' để bắt đầu cuộc trò chuyện mới\n")
    
    while True:
        user_input = input("Bạn: ")
        
        if user_input.lower() == 'exit':
            print("Tạm biệt!")
            break
        
        if user_input.lower() == 'reset':
            assistant.reset_conversation()
            continue
        
        if user_input.strip() == '':
            continue
        
        # Gửi tin nhắn và nhận phản hồi
        response = assistant.send_message(user_input)
        print(f"\nTrợ lý: {response}\n")