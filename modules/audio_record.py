import speech_recognition as sr
import os
from config import settings

class Recorder:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Tăng độ nhạy mic
        # Tắt tự động căn chỉnh để tránh bị tiếng quạt làm nhiễu
        self.recognizer.dynamic_energy_threshold = False
        
        self.recognizer.energy_threshold = 350 
        self.recognizer.pause_threshold = 2.0 # Ngừng nói 2s là ngắt
        # 4. Bỏ qua các âm thanh quá ngắn (dưới 0.5s) -> Coi là tiếng gõ phím/ho
        self.recognizer.phrase_threshold = 0.5 

    def listen(self):
        """Nghe và lưu ra file .wav, trả về đường dẫn file"""
        print("\n🎤 Đang nghe...")
        
        try:
            with sr.Microphone() as source:
                #self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # timeout: Chờ 5s không nói gì thì thôi
                # self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                
                # Lưu file tạm vào thư mục logs
                file_path = os.path.join(settings.LOGS_DIR, "command.wav")
                with open(file_path, "wb") as f:
                    f.write(audio.get_wav_data())
                
                return file_path

        except sr.WaitTimeoutError:
            print("zzz... Hết giờ chờ.")
            return None
        except Exception as e:
            print(f"❌ Lỗi ghi âm: {e}")
            return None