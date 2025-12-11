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
        self.voices = ["vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural"]
        self.output_file = os.path.join(settings.LOGS_DIR, "response_edge.mp3")
        self.disabled = False

    async def _generate_audio(self, text, voice):
        """Hàm chạy ngầm để tải file âm thanh về"""
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(self.output_file)

    def speak(self, text):
        if not text or self.disabled:
            return
        print(f"TTS: {text}")
        try:
            # 1. Gọi hàm async để tạo file mp3 (thử lần lượt các voice)
            last_err = None
            success = False
            for voice in self.voices:
                try:
                    asyncio.run(self._generate_audio(text, voice))
                    success = True
                    break
                except Exception as e:
                    last_err = e
                    continue
            if not success:
                # Nếu Edge TTS không dùng được (thường do mất mạng/voice sai), tắt để tránh spam lỗi
                self.disabled = True
                print(f"❌ Lỗi Edge TTS: {last_err} - tạm tắt Edge TTS (cần mạng hoặc tên voice hợp lệ).")
                return
            
            # 2. Phát âm thanh
            if os.path.exists(self.output_file):
                data, fs = sf.read(self.output_file)
                sd.play(data, fs)
                sd.wait()
            else:
                print("❌ Lỗi: Không tạo được file âm thanh.")
                
        except Exception as e:
            print(f"❌ Lỗi Edge TTS: {e} - kiểm tra kết nối Internet hoặc tên voice.")
