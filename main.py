import os
import time
import requests
from pydub import AudioSegment
from pydub.effects import normalize
from gtts import gTTS  # Dùng Google TTS trực tiếp

# Import các module
from modules.esp32_mic import ESP32Mic
from modules.stt_whisper import STTEngine
from modules.nlu_engine import NLUEngine
from modules.skills import SkillEngine

# ======================
#   CẤU HÌNH (SỬA IP TẠI ĐÂY)
# ======================
ESP32_PORT = 5000 
HA_URL = "http://homeassistant.local:8123/"  # <--- SỬA DÒNG NÀY
# Token của bạn lấy từ homneassistant
TOKEN = ""

HA_LIGHT_MAP = {
    "living_light": "light.phong_khach",
    "bed_light": "light.phong_ngu",
    "kitchen_light": "light.nha_bep"
}

# ======================
#   XỬ LÝ ÂM THANH
# ======================
def convert_to_esp32_format(input_file, output_file="esp32_out.wav"):
    """
    Convert âm thanh sang chuẩn WAV 16kHz, 16bit, Mono cho ESP32.
    """
    try:
        if not os.path.exists(input_file):
            print("❌ Lỗi: Không tìm thấy file đầu vào.")
            return None

        audio = AudioSegment.from_file(input_file)
        # 1. Kích âm lượng
        audio = normalize(audio)
        # 2. Ép chuẩn 16k Mono
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        audio.export(output_file, format="wav")
        return output_file
    except Exception as e:
        print(f"❌ Lỗi Convert Audio (Cần cài FFmpeg): {e}")
        return None
class HomeAssistantClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def turn_on_light(self, entity_id): return self._call("light", "turn_on", entity_id)
    def turn_off_light(self, entity_id): return self._call("light", "turn_off", entity_id)

    def _call(self, domain, service, entity_id):
        url = f"{self.base_url}/api/services/{domain}/{service}"
        print(f"🔌 Gọi HA: {service} -> {entity_id}")
        try:
            resp = requests.post(url, headers=self.headers, json={"entity_id": entity_id}, timeout=3)
            if resp.status_code == 200:
                print("✅ HA: Thành công!")
                return True
            else:
                print(f"❌ HA Lỗi: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            print(f"❌ Lỗi kết nối HA: {e}")
            return False

# ======================
#   HỖ TRỢ
# ======================
VALID_LOCATIONS = ["living_room", "bedroom", "kitchen"]
TTS_LOCATION = {"living_room": "phòng khách", "bedroom": "phòng ngủ", "kitchen": "nhà bếp", None: "phòng khách"}

def get_device_id(device_type, location):
    prefix = {"living_room": "living", "bedroom": "bed", "kitchen": "kitchen"}.get(location, "living")
    return f"{prefix}_{device_type}"

# ======================
#   MAIN LOOP
# ======================
def run_ai_logic():
    print("🚀 AI System Starting...")
    try:
        recorder = ESP32Mic(port=ESP32_PORT)
        stt = STTEngine()
        nlu = NLUEngine()
        skills = SkillEngine()
        ha = HomeAssistantClient(HA_URL, TOKEN)
        print(f"✅ System Ready! Port {ESP32_PORT}")
    except Exception as e:
        print(f"❌ Lỗi Khởi tạo: {e}")
        return

    while True:
        try:
            print("\n🎧 Đang chờ lệnh từ ESP32...")
            
            # 1. Nhận Audio
            audio_path = recorder.listen()
            print(f"🎤 Nhận file: {audio_path}")

            # 2. STT
            text = stt.transcribe(audio_path)
            if not text:
                print("❌ Không nghe rõ")
                continue
            print(f"🗣 User: {text}")

            # 3. NLU
            commands = nlu.predict(text)
            response_text = ""
            
            if not commands:
                response_text = "Xin lỗi, tôi chưa hiểu."
            else:
                # NLU có thể trả về nhiều lệnh (VD: Chào + Bật đèn)
                for cmd in commands:
                    intent = cmd.get("intent")
                    location = cmd.get("location") 
                    
                    # --- XỬ LÝ CHÀO HỎI (MỚI THÊM) ---
                    if intent == "greet":
                        response_text += "Chào bạn, tôi có thể giúp gì? "

                    # --- XỬ LÝ ĐÈN ---
                    elif intent in ["turn_on", "turn_off"]:
                        if location not in VALID_LOCATIONS:
                            response_text += "Bạn muốn bật đèn ở đâu? "
                            continue
                        
                        target_id = get_device_id("light", location)
                        ha_entity = HA_LIGHT_MAP.get(target_id)
                        
                        if ha_entity:
                            if intent == "turn_on": ha.turn_on_light(ha_entity)
                            else: ha.turn_off_light(ha_entity)
                        else:
                            print(f"⚠️ Không tìm thấy Entity ID: {target_id}")

                        # Gửi lệnh Relay
                        recorder.send_command(f"{target_id}:{'ON' if intent == 'turn_on' else 'OFF'}")
                        
                        loc_vn = TTS_LOCATION.get(location)
                        act_vn = "bật" if intent == "turn_on" else "tắt"
                        response_text += f"Đã {act_vn} đèn {loc_vn}. "
                        
                    # --- SKILLS KHÁC ---
                    elif intent == "ask_time": response_text += f"Bây giờ là {skills.get_time()}. "
                    elif intent == "ask_date": response_text += skills.get_date()
                    elif intent == "ask_weather": response_text += skills.get_weather()
            if not response_text: response_text = "Đã thực hiện."
            print(f"🤖 Bot: {response_text}")

            # 4. TTS & GỬI ÂM THANH
            try:
                temp_mp3 = "response_temp.mp3"
                final_wav = "response_final.wav"
                
                # Tạo giọng nói Google
                tts = gTTS(text=response_text, lang='vi')
                tts.save(temp_mp3)

                # Convert và Gửi
                if os.path.exists(temp_mp3):
                    valid_wav = convert_to_esp32_format(temp_mp3, final_wav)
                    if valid_wav:
                        with open(valid_wav, "rb") as f:
                            wav_data = f.read()
                        recorder.send_audio(wav_data)
                    else:
                        print("❌ Lỗi convert âm thanh.")
                else:
                    print("⚠️ Lỗi tạo file TTS.")

            except Exception as e:
                print(f"❌ Lỗi TTS: {e}")

        except KeyboardInterrupt:
            print("\n⛔ Dừng hệ thống.")
            break
        except Exception as e:
            print(f"❌ Lỗi vòng lặp: {e}")
            time.sleep(1)

if __name__ == "__main__":
    run_ai_logic()