import edge_tts
import asyncio
import os
from config import settings

class TTSEngine:
    def __init__(self):
        # Chọn giọng: 
        # "vi-VN-HoaiMyNeural" (Nữ - Rất hay)
        # "vi-VN-NamMinhNeural" (Nam - Rất hay)
        self.voice = "vi-VN-HoaiMyNeural"
        
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(settings.LOGS_DIR):
            os.makedirs(settings.LOGS_DIR)
            
        self.output_file = os.path.join(settings.LOGS_DIR, "response_edge.mp3")
        
    async def _generate_audio(self, text):
        """Hàm chạy ngầm để tải file âm thanh về"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(self.output_file)

    def speak(self, text):
        """
        Tạo file âm thanh và TRẢ VỀ ĐƯỜNG DẪN FILE (để gửi xuống ESP32)
        """
        if not text:
            return None
            
        print(f"TTS Generating: {text}")
        
        try:
            # 1. Gọi hàm async để tạo file mp3
            asyncio.run(self._generate_audio(text))
            
            # 2. Kiểm tra xem file có được tạo thành công không
            if os.path.exists(self.output_file):
                # QUAN TRỌNG: Trả về đường dẫn file để main.py gửi xuống ESP32
                # KHÔNG dùng sounddevice để phát ở đây nữa
                return self.output_file 
            else:
                print("❌ Lỗi: Không tạo được file âm thanh.")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi Edge TTS: {e}")
            return None
