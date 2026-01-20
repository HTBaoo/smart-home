import asyncio
import websockets
import threading
import json

# --- CẤU HÌNH ---
PORT = 8765
connected_clients = set()
loop = None

# --- LƯU TRỮ TRẠNG THÁI THIẾT BỊ (Shared State) ---
# Đây là nơi duy nhất chứa sự thật: Đèn đang tắt hay mở?
device_states = {
    "light": "OFF",
    "curtain": "CLOSE",
    "door":"CLOSE"
}

# Callback để gọi cập nhật giao diện bên Dashboard (sẽ được gán từ main)
update_ui_callback = None

def set_ui_callback(callback_func):
    global update_ui_callback
    update_ui_callback = callback_func

async def handler(websocket):
    """Xử lý kết nối từ Web hoặc ESP8266"""
    print(f"🔗 Client kết nối: {websocket.remote_address}")
    connected_clients.add(websocket)
    
    # 1. Khi vừa kết nối, gửi ngay trạng thái hiện tại cho Client đó
    # Để web/app trên điện thoại vừa mở lên là thấy đúng trạng thái ngay
    try:
        await websocket.send(json.dumps({"type": "sync_state", "data": device_states}))
        
        async for message in websocket:
            print(f"📩 Nhận từ Client: {message}")
            try:
                data = json.loads(message)
                
                # Nếu nhận được lệnh điều khiển (từ Web hoặc ESP vật lý)
                if "device" in data and "state" in data:
                    device = data["device"]
                    state = data["state"]
                    
                    # Cập nhật trạng thái server
                    device_states[device] = state
                    
                    # Đồng bộ lại cho TẤT CẢ các client khác (Web, ESP, App)
                    await broadcast_message(json.dumps(data))
                    
                    # Cập nhật giao diện NiceGUI trên máy chủ (Laptop)
                    if update_ui_callback:
                        update_ui_callback(device, state)
                    #await broadcast_message(json.dumps(data))
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

async def run_server():
    print(f"🚀 WebSocket Hub đang chạy tại ws://0.0.0.0:{PORT}")
    async with websockets.serve(handler, "0.0.0.0", PORT):
        await asyncio.Future()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_server())

def start():
    """Khởi động Server"""
    global loop
    if loop and loop.is_running():
        return
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(loop,), daemon=True)
    t.start()

def send_command(device_id, state, location="living_room"):
    """
    Hàm dùng cho AI (Python) gọi để điều khiển.
    Nó sẽ cập nhật trạng thái và bắn tín hiệu đi.
    """
    global loop
    
    # Cập nhật trạng thái nội bộ
    device_states[device_id] = state
    
    # Tạo gói tin
    payload = {
        "device": device_id,
        "state": state,
        "location": location,
        "source": "AI"
    }
    
    # Gửi đi
    if loop and loop.is_running():
        msg = json.dumps(payload)
        asyncio.run_coroutine_threadsafe(broadcast_message(msg), loop)
        
    # Cập nhật UI Laptop
    if update_ui_callback:
        update_ui_callback(device_id, state)

async def broadcast_message(message):
    if connected_clients:
        await asyncio.gather(*(client.send(message) for client in connected_clients), return_exceptions=True)
# import asyncio
# import websockets
# import threading
# import json

# # --- CẤU HÌNH ---
# PORT = 8765
# connected_clients = set()
# loop = None

# # --- TRẠNG THÁI THIẾT BỊ (Shared State) ---
# device_states = {
#     "light": "OFF",
#     "curtain": "CLOSE",
#     "door": "CLOSE",
#     "fan": "OFF"
# }

# # Callback để update UI (NiceGUI)
# update_ui_callback = None

# def set_ui_callback(callback_func):
#     """Dashboard đăng ký callback UI"""
#     global update_ui_callback
#     update_ui_callback = callback_func

# # ================== WEBSOCKET CORE ==================

# async def handler(websocket):
#     print(f"🔗 Client kết nối: {websocket.remote_address}")
#     connected_clients.add(websocket)

#     try:
#         # Sync trạng thái ban đầu
#         await websocket.send(json.dumps({
#             "type": "sync_state",
#             "data": device_states
#         }))

#         async for message in websocket:
#             print(f"📩 Nhận: {message}")
#             try:
#                 data = json.loads(message)

#                 if "device" in data and "state" in data:
#                     device = data["device"]
#                     state = data["state"]
#                     location = data.get("location")
#                     source = data.get("source", "client")

#                     # Update state
#                     device_states[device] = state

#                     payload = {
#                         "device": device,
#                         "state": state,
#                         "location": location,
#                         "source": source
#                     }

#                     # Broadcast
#                     await broadcast_message(json.dumps(payload))

#                     # Update UI local (NiceGUI)
#                     if update_ui_callback:
#                         update_ui_callback(device, state)

#             except json.JSONDecodeError:
#                 print("⚠️ JSON lỗi")

#     except websockets.exceptions.ConnectionClosed:
#         print("❌ Client ngắt kết nối")

#     finally:
#         connected_clients.discard(websocket)

# async def broadcast_message(message):
#     if connected_clients:
#         await asyncio.gather(
#             *(client.send(message) for client in connected_clients),
#             return_exceptions=True
#         )

# async def run_server():
#     print(f"🚀 WebSocket Hub chạy tại ws://0.0.0.0:{PORT}")
#     async with websockets.serve(handler, "0.0.0.0", PORT):
#         await asyncio.Future()  # chạy vĩnh viễn

# def _start_loop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(run_server())

# # ================== PUBLIC API (GIỮ NGUYÊN) ==================

# def start():
#     """
#     Được gọi từ dashboard.py
#     Khởi động websocket server ở thread riêng
#     """
#     global loop
#     if loop and loop.is_running():
#         return

#     loop = asyncio.new_event_loop()
#     t = threading.Thread(
#         target=_start_loop,
#         args=(loop,),
#         daemon=True
#     )
#     t.start()

# def send_command(device_id, state, location=None):
#     """
#     Được gọi từ:
#     - Dashboard
#     - AI
#     - Whisper
#     """
#     global loop

#     device_states[device_id] = state

#     payload = {
#         "device": device_id,
#         "state": state,
#         "location": location,
#         "source": "python"
#     }

#     if loop and loop.is_running():
#         asyncio.run_coroutine_threadsafe(
#             broadcast_message(json.dumps(payload)),
#             loop
#         )

#     # Update UI local
#     if update_ui_callback:
#         update_ui_callback(device_id, state)
