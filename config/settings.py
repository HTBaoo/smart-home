import os

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- CẤU HÌNH ĐƯỜNG DẪN ---
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Tạo thư mục logs nếu chưa có
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# 1. STT (Whisper Custom)
STT_MODEL_PATH = os.path.join(MODELS_DIR, "stt_whisper")

# # 2. TTS (Piper)
# # Lưu ý: Sửa tên file exe và model cho đúng thực tế máy bạn
PIPER_DIR = os.path.join(MODELS_DIR, "tts_piper")
PIPER_EXE_PATH = os.path.join(PIPER_DIR, "piper.exe") 
TTS_MODEL_PATH = os.path.join(PIPER_DIR, "vi_VN-25hours_single-low.onnx") 

# 3. NLU (Intent)
NLU_MODEL_PATH = os.path.join(MODELS_DIR, "nlu", "intent_model.joblib")
NLU_VECTORIZER_PATH = os.path.join(MODELS_DIR, "nlu", "tfidf.joblib")


# --- CẤU HÌNH MQTT ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "home/control"