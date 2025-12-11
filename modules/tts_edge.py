import edge_tts
import asyncio
import os
import sounddevice as sd
import soundfile as sf
from config import settings

class TTSEngine:
    def __init__(self):
        # Chọn giọng: 
        # "vi-VN-HoaiMyNeural" (Nữ - Rất hay)
        # "vi-VN-NamMinhNeural" (Nam - Rất hay)
        self.voice = "vi-VN-HoaiMyNeural"
        self.output_file = os.path.join(settings.LOGS_DIR, "response_edge.mp3")

    async def _generate_audio(self, text):
        """Hàm chạy ngầm để tải file âm thanh về"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(self.output_file)

    def speak(self, text):
        print(f"TTS: {text}")
        try:
            # 1. Gọi hàm async để tạo file mp3
            asyncio.run(self._generate_audio(text))
            
            # 2. Phát âm thanh
            if os.path.exists(self.output_file):
                data, fs = sf.read(self.output_file)
                sd.play(data, fs)
                sd.wait()
            else:
                print("❌ Lỗi: Không tạo được file âm thanh.")
                
        except Exception as e:
            print(f"❌ Lỗi Edge TTS: {e}")
