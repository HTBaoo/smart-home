from faster_whisper import WhisperModel
import os
from config import settings

class STTEngine:
    def __init__(self):
        print(f"⏳ Đang tải Whisper Custom từ: {settings.STT_MODEL_PATH}")
        
        if not os.path.exists(settings.STT_MODEL_PATH):
            print(f"⚠️ CẢNH BÁO: Không thấy model tại {settings.STT_MODEL_PATH}")
            print("👉 Hãy copy folder 'whisper-smarthome-ct2' vào models/stt_whisper")
        
        # int8 cho nhẹ máy
        self.model = WhisperModel(settings.STT_MODEL_PATH, device="cpu", compute_type="int8")
        print("✅ Whisper đã sẵn sàng!")

    def transcribe(self, audio_path):
        if not audio_path or not os.path.exists(audio_path):
            return ""
        
        try:
            segments, _ = self.model.transcribe(audio_path, language="vi",vad_filter=True)
            # segments, _ = self.model.transcribe(audio_path, beam_size=1, language="vi",vad_filter=True)
            text = "".join([s.text for s in segments]).strip()
            black_list = [
                "subtitle by", "amara.org", "cảm ơn", "vietsub", 
                "xem video", "đăng ký kênh", "copyright", "hãy like"
            ]
            for word in black_list:
                if word in text:
                    return ""
            return text.lower()
        except Exception as e:
            print(f"❌ Lỗi STT: {e}")
            return ""