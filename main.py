import threading
from nicegui import ui

# ======================
#   IMPORT MODULES
# ======================
import modules.websocket_server as ws_server
import modules.dashboard as dashboard

from modules.audio_record import Recorder
from modules.stt_whisper import STTEngine
from modules.nlu_engine import NLUEngine
from modules.skills import SkillEngine
from modules.tts_edge import TTSEngine
LOCATION_ID = {
    "living_room": "living",  # living_light
    "bedroom": "bed",         # bed_light
    "kitchen": "kitchen",     # kitchen_light
    "bathroom": "bath",
    "all": "all",
    None: "living"            # Mặc định
}
LOCATION_VN = {
    "living_room": "phòng khách",
    "bedroom": "phòng ngủ",
    "kitchen": "nhà bếp",
    "bathroom": "nhà tắm",
    "all": "toàn bộ căn nhà",
    "unknown": ""
            }
ALL_ROOM_PREFIXES = ["living", "bed", "kitchen"]
CONTROLL_VN = { "ON" : "bật", "OFF" : "tắt", "OPEN" : "mở", "CLOSE" : "đóng" }
# ======================
#   1. KHỞI TẠO UI
# ======================
dashboard.init_interface()
# ======================
#   2. CALLBACK ĐỒNG BỘ
# ======================
def on_state_change(device, state):
    """Callback từ WebSocket khi ESP gửi trạng thái về."""
    dashboard.update_ui_from_state(device, state)
    dashboard.add_log(f"Đồng bộ: {device} → {state}")


ws_server.set_ui_callback(on_state_change)

# hàm lấy ID 
def get_device_id(device_type, location):
    prefix = LOCATION_ID.get(location, "living")
    return f"{prefix}_{device_type}"
# ======================
#   3. AI BACKGROUND THREAD
# ======================
def run_ai_logic():
    print("🚀 AI Thread bắt đầu...")

    try:
        # --- BẮT ĐẦU SERVER WebSocket ---
        ws_server.start()

        # --- MODULE AI ---
        recorder = Recorder()
        stt = STTEngine()         # 🟢 Bạn sẽ gắn Whisper retrain ở đây
        nlu = NLUEngine()
        # tts = TTSEdgeEngine()
        skills = SkillEngine()
        tts = TTSEngine()
        dashboard.add_log("Tôi đã sẵn sàng")
        tts.speak("Tôi đã sẵn sàng.")

    except Exception as e:
        print(f"Lỗi khởi động AI: {e}")
        return

    # --- VÒNG LẶP XỬ LÝ GIỌNG NÓI ---
    while True:
        try:
            audio_path = recorder.listen()
            if not audio_path:
                continue
            # --- STT: Speech → Text ---
            text = stt.transcribe(audio_path)
            if not text:
                continue
            dashboard.add_log(f"Bạn nói: {text}")
            # --- NLU ---
            commands = nlu.predict(text)
            if not commands:
                tts.speak("Xin lỗi, tôi chưa hiểu.")
                continue
            # --- XỬ LÝ LỆNH ---

            response_text = ""

            for cmd in commands:
                intent = cmd.get("intent")
                location = cmd.get("location") or "living_room"
                vn_loc = LOCATION_VN.get(location, "")
                
                target_id = None
                action = None
                device_name = ""
                
                # if intent == "turn_on":
                #     response_text += f"Đã bật đèn {vn_loc}"
                #     target_id = get_device_id("light", location)
                #     action = "ON" 
                #     device_name = "đèn"
                #     ws_server.send_command("light", "ON", location)
                # elif intent == "turn_off":
                #     response_text += f"Đã tắt đèn {vn_loc} "
                #     ws_server.send_command("light", "OFF", location)
                # elif intent == "open_curtain":
                #     response_text += f"Đang mở rèm {vn_loc} "
                #     ws_server.send_command("curtain", "OPEN", location)
                # elif intent == "close_curtain":
                #     response_text += f"Đang đóng rèm {vn_loc} "
                #     ws_server.send_command("curtain", "CLOSE", location)
                if intent in ["turn_on", "turn_off"]:
                    # Mặc định là đèn, nếu muốn mở rộng quạt thì thêm logic check text
                    target_id = get_device_id("light", location)
                    action = "ON" if intent == "turn_on" else "OFF"
                    device_name_vn = "đèn"

                elif intent in ["open_curtain", "close_curtain"]:
                    target_id = get_device_id("curtain", location)
                    action = "OPEN" if intent == "open_curtain" else "CLOSE"
                    device_name_vn = "rèm"

                # --- GỬI LỆNH XUỐNG WEBSOCKET ---
                if target_id and action:
                    # 1. Gửi xuống WebSocket (Broadcast cho ESP32 & Web)
                    # Hàm này trong ws_server cần nhận ID chuẩn (vd: bed_light)
                    ws_server.send_command(target_id, action)
                    controll = CONTROLL_VN.get(action)
                    # 2. Tạo câu phản hồi
                    state_vn = f"{controll}" 
                    # if action in ["ON", "OPEN"] 
                    # else state_vn = f"{controll}"
                    response_text += f"Đã {state_vn} {device_name_vn} {vn_loc}. "
                    
                    # 3. Cập nhật UI ngay lập tức cho mượt (Optimistic UI)
                    dashboard.update_ui_from_state(target_id, action)
                elif intent == "ask_weather":
                    response_text += f"{skills.get_weather()}."
                elif intent == "ask_time":
                    response_text += f"Bây giờ là {skills.get_time()}."
                elif intent == "ask_date":
                    response_text += f"{skills.get_date()}."
                elif intent == "play_music":
                    response_text += f"{skills.play_music()}"
            if response_text:
                tts.speak(response_text)

        except Exception as e:
            # Không để AI thread chết
            dashboard.add_log(f"⚠ Lỗi AI loop: {e}")
            continue


# ======================
#   4. CHẠY CHƯƠNG TRÌNH
# ======================
ui.timer(
    0.1,
    lambda: threading.Thread(target=run_ai_logic, daemon=True).start(),
    once=True,
)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Smart Home Hub", host="0.0.0.0", port=8888, reload=False)
