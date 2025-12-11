# from nicegui import ui
# import json
# import asyncio
# import websockets

# # Import module websocket để gửi lệnh đi
# import modules.websocket_server as ws_server

# # Biến toàn cục để lưu tham chiếu tới các thẻ UI để cập nhật sau này
# ui_elements = {}

# def init_interface():
#     """Hàm vẽ giao diện chính"""
    
#     # --- STYLE ---
#     #ui.colors(primary='#5898d4', secondary='#26a69a', accent='#9c27b0', dark='#1d1d1d')
#     ui.colors(primary='#5898d4',  dark='#1d1d1d')
#     ui.query('body').style('background-color: #121212; color: white;')

#     with ui.header().classes('bg-gray-900 items-center justify-between'):
#         ui.label('🏠 SMART HOME CONTROL').classes('text-xl font-bold text-white')
#         ui.label('Online').classes('text-green-400 font-bold')

#     # --- CONTAINER ---
#     # with ui.row().classes('w-full justify-center gap-6 q-pa-md'):
#     with ui.card().classes('w-full justify-center gap-6 q-pa-md'):
#         ui.label('📍 Phòng Khách').classes('text-x1 font-bold mb-3')
#         with ui.row().classes('gap-6'):
            
#         # 1. THẺ ĐÈN (Có sự kiện on_click)
#             # with ui.card().classes('w-48 items-center bg-gray-800 border-2 border-gray-600 cursor-pointer transition-all') as light_card:
#             with ui.card().classes('w-48 items-center bg-gray-900 cursor-pointer border border-gray-700') as light1_card:
#                 ui.icon('lightbulb', size='3em').classes('text-yellow-500')
#                 ui.label('Đèn Phòng Khách').classes('text-lg font-bold mt-2')
#                 light1_status = ui.label('OFF').classes('text-xl font-bold text-gray-400')
#             # Sự kiện bấm vào thẻ -> Gửi lệnh Toggle
#                 light1_card.on('click', lambda: toggle_device('light', light1_status.text))

#         # 2. THẺ RÈM
#             with ui.card().classes('w-48 items-center bg-gray-800 border-2 border-gray-600 cursor-pointer transition-all') as curtain1_card:
#                 ui.icon('curtains', size='4em').classes('text-gray-500')
#                 ui.label('Rèm Cửa').classes('text-lg font-bold mt-2')
#                 curtain1_status = ui.label('ĐÓNG').classes('text-xl font-bold text-gray-400')
            
#                 curtain1_card.on('click', lambda: toggle_device('curtain', curtain1_status.text))
#     with ui.card().classes('w-full justify-center gap-6 q-pa-md'):
#         ui.label('📍 Phòng Ngủ').classes('text-x1 font-bold mb-3')
#         with ui.row().classes('gap-6'):
            
#         # 1. THẺ ĐÈN (Có sự kiện on_click)
#             with ui.card().classes('w-48 items-center bg-gray-800 border-2 border-gray-600 cursor-pointer transition-all') as light2_card:
#                 ui.icon('lightbulb', size='4em').classes('text-gray-500')
#                 ui.label('Đèn Phòng Khách').classes('text-lg font-bold mt-2')
#                 light2_status = ui.label('OFF').classes('text-xl font-bold text-gray-400')
#             # Sự kiện bấm vào thẻ -> Gửi lệnh Toggle
#                 light2_card.on('click', lambda: toggle_device('light', light2_status.text))

#         # 2. THẺ RÈM
#             with ui.card().classes('w-48 items-center bg-gray-800 border-2 border-gray-600 cursor-pointer transition-all') as curtain2_card:
#                 ui.icon('curtains', size='4em').classes('text-gray-500')
#                 ui.label('Rèm Cửa').classes('text-lg font-bold mt-2')
#                 curtain2_status = ui.label('ĐÓNG').classes('text-xl font-bold text-gray-400')
            
#                 curtain2_card.on('click', lambda: toggle_device('curtain', curtain2_status.text))
#     # Lưu tham chiếu để dùng ở hàm update
#     ui_elements['light1_card'] = light1_card
#     ui_elements['light1_status'] = light1_status
#     ui_elements['light2_card'] = light2_card
#     ui_elements['light2_status'] = light2_status
#     ui_elements['curtain1_card'] = curtain1_card
#     ui_elements['curtain1_status'] = curtain1_status
#     ui_elements['curtain2_card'] = curtain2_card
#     ui_elements['curtain2_status'] = curtain2_status

#     # --- LOG BOX ---
#     ui.separator().classes('bg-gray-700 my-4')
#     with ui.scroll_area().classes('w-full h-48 bg-black p-4 border border-gray-700 rounded-lg mx-4') as log_area:
#         ui_elements['log_container'] = ui.column().classes('w-full')
#         ui_elements['log_area'] = log_area

# def toggle_device(device, current_state):
#     """Xử lý khi người dùng click trên Web"""
#     new_state = ""
#     if device == "light":
#         new_state = "ON" if current_state == "OFF" else "OFF"
#     elif device == "curtain":
#         new_state = "OPEN" if current_state == "ĐÓNG" else "CLOSE" # Logic map tên
        
#     # Gửi lệnh vào Server -> Server sẽ broadcast lại cho ESP và Web
#     ws_server.send_command(device, new_state)

# def update_ui_from_state(device, state):
#     """
#     Hàm này được gọi từ Main hoặc WebSocket Server khi trạng thái thay đổi.
#     Nó chịu trách nhiệm thay đổi màu sắc icon.
#     """
#     # Vì hàm này được gọi từ Thread khác, cần wrap trong ui.context hoặc cẩn thận.
#     # Tuy nhiên NiceGUI thread-safe khá tốt nếu dùng properties.
    
#     if device == "light":
#         card = ui_elements['light_card']
#         lbl = ui_elements['light_status']
#         if state == "ON":
#             card.classes(remove='border-gray-600', add='border-yellow-400 shadow-lg shadow-yellow-500/50')
#             lbl.text = 'ON'
#             lbl.classes(remove='text-gray-400', add='text-yellow-400')
#         else:
#             card.classes(remove='border-yellow-400 shadow-lg shadow-yellow-500/50', add='border-gray-600')
#             lbl.text = 'OFF'
#             lbl.classes(remove='text-yellow-400', add='text-gray-400')
            
#     elif device == "curtain":
#         card = ui_elements['curtain_card']
#         lbl = ui_elements['curtain_status']
#         # Map state OPEN/CLOSE sang hiển thị MỞ/ĐÓNG
#         display_text = "MỞ" if state == "OPEN" else "ĐÓNG"
        
#         if state == "OPEN":
#             card.classes(remove='border-gray-600', add='border-blue-400 shadow-lg shadow-blue-500/50')
#             lbl.text = display_text
#             lbl.classes(remove='text-gray-400', add='text-blue-400')
#         else:
#             card.classes(remove='border-blue-400 shadow-lg shadow-blue-500/50', add='border-gray-600')
#             lbl.text = display_text
#             lbl.classes(remove='text-blue-400', add='text-gray-400')

# def add_log(text):
#     with ui_elements['log_container']:
#         ui.label(f"> {text}").classes('text-green-400 font-mono text-sm')
#     ui_elements['log_area'].scroll_to(percent=1.0)
from nicegui import ui
import modules.websocket_server as ws_server

# --- CẤU HÌNH NHÀ THÔNG MINH (Dữ liệu nguồn) ---
# Bạn thêm phòng hoặc thiết bị ở đây dễ dàng
HOME_CONFIG = [
    {
      "room_name" : "Sảnh",
      "devices" :[
            {"id": "lobby_light", "name": "Đèn sảnh", "type": "light", "state": "OFF"},
            {"id": "lobby_door", "name": "Cửa chính", "type": "door", "state": "ĐÓNG"}
      ]  
    },
    {
        "room_name": "Phòng Khách",
        "devices": [
            {"id": "living_light", "name": "Đèn Trần", "type": "light", "state": "OFF"},
            {"id": "living_curtain", "name": "Rèm Cửa", "type": "curtain", "state": "ĐÓNG"},
            {"id": "living_fan", "name": "Quạt Trần", "type": "fan", "state": "OFF"} # Thử thêm quạt
        ]
    },
    {
        "room_name": "Phòng Ngủ",
        "devices": [
            {"id": "bed_light", "name": "Đèn Ngủ", "type": "light", "state": "OFF"},
            {"id": "bed_curtain", "name": "Rèm Cửa Sổ", "type": "curtain", "state": "ĐÓNG"}
        ]
    },
     {
        "room_name": "Nhà Bếp", 
        "devices": [
            {"id": "kitchen_light", "name": "Đèn Bếp", "type": "light", "state": "OFF"}
        ]
    }
]

# Lưu tham chiếu UI để update sau này (Key sẽ là device_id)
ui_refs = {} 

def init_interface():
    """Hàm vẽ giao diện chính dựa trên HOME_CONFIG"""
    
    # --- STYLE ---
    ui.colors(primary='#5898d4', dark='#1d1d1d')
    ui.query('body').style('background-color: #121212; color: white;')

    with ui.header().classes('bg-gray-900 items-center justify-between'):
        ui.label('🏠 SMART HOME CONTROL').classes('text-xl font-bold text-white')
        ui.label('Online').classes('text-green-400 font-bold')

    # --- RENDER GIAO DIỆN TỪ CONFIG ---
    # Lặp qua từng phòng
    for room in HOME_CONFIG:
        with ui.card().classes('w-full q-pa-md bg-gray-900 border border-gray-700 mb-4'):
            ui.label(f"📍 {room['room_name']}").classes('text-xl font-bold mb-3 text-blue-400')
            
            with ui.row().classes('gap-6 wrap'):
                # Lặp qua từng thiết bị trong phòng
                for device in room['devices']:
                    create_device_card(device)

    # --- LOG BOX ---
    ui.separator().classes('bg-gray-700 my-4')
    with ui.scroll_area().classes('w-full h-48 bg-black p-4 border border-gray-700 rounded-lg mx-4') as log_area:
        ui_refs['log_container'] = ui.column().classes('w-full')
        ui_refs['log_area'] = log_area

def create_device_card(device_info):
    """
    Hàm này tạo 1 thẻ UI cho 1 thiết bị cụ thể.
    device_info: dictionary chứa {id, name, type, state}
    """
    d_id = device_info['id']
    d_type = device_info['type']
    d_name = device_info['name']
    d_state = device_info['state']

    # Chọn icon dựa trên loại thiết bị
    icon_name = 'help'
    if d_type == 'light': icon_name = 'lightbulb'
    elif d_type == 'curtain': icon_name = 'curtains'
    elif d_type == 'fan': icon_name = 'wind_power'
    elif d_type == 'door': icon_name = 'meeting_room'

    # Vẽ thẻ
    with ui.card().classes('w-48 items-center bg-gray-800 border border-gray-600 cursor-pointer transition-all hover:bg-gray-700') as card:
        icon_ui = ui.icon(icon_name, size='3em').classes('text-gray-500')
        ui.label(d_name).classes('text-lg font-bold mt-2 text-center')
        status_ui = ui.label(d_state).classes('text-xl font-bold text-gray-400')

    # --- QUAN TRỌNG: Lưu tham chiếu vào Dictionary toàn cục ---
    ui_refs[d_id] = {
        'card': card,
        'status_label': status_ui,
        'icon': icon_ui,
        'type': d_type
    }

    # --- SỰ KIỆN CLICK ---
    # Dùng lambda nhưng phải gán ID hiện tại vào biến cục bộ để tránh lỗi closure trong vòng lặp
    card.on('click', lambda: handle_click(d_id))

def handle_click(device_id):
    """Xử lý khi click vào bất kỳ thẻ nào"""
    # Lấy trạng thái hiện tại từ UI (hoặc từ biến lưu trữ nếu có)
    current_text = ui_refs[device_id]['status_label'].text
    d_type = ui_refs[device_id]['type']
    
    # Logic đảo trạng thái
    new_state = ""
    if d_type == "light" or d_type == "fan":
        new_state = "ON" if current_text == "OFF" else "OFF"
    elif d_type == "curtain" or d_type == "door":
        new_state = "OPEN" if current_text == "ĐÓNG" else "CLOSE"

    # Gọi hàm gửi lệnh chung
    send_command_to_server(device_id, new_state)

def send_command_to_server(device_id, state):
    """Gửi lệnh xuống WebSocket Server"""
    # Tạo payload có cấu trúc rõ ràng
    # Ví dụ: {"id": "living_light", "cmd": "ON"}
    add_log(f"Sending to {device_id}: {state}")
    ws_server.send_command(device_id, state)
    # Gọi module websocket của bạn
    # ws_server.send_command(device_id, state) 
    
    # Tạm thời giả lập phản hồi ngay lập tức để test UI (Thực tế server sẽ gọi lại update_ui)
    update_ui_from_state(device_id, state)

def update_ui_from_state(device_id, state):
    """
    Cập nhật UI của 1 thiết bị cụ thể dựa trên ID.
    Hàm này có thể được gọi từ Websocket Server khi ESP32 phản hồi.
    """
    if device_id not in ui_refs:
        print(f"Không tìm thấy UI cho thiết bị: {device_id}")
        return

    elements = ui_refs[device_id]
    card = elements['card']
    lbl = elements['status_label']
    d_type = elements['type']

    # Logic hiển thị theo loại thiết bị
    if d_type == "light" or d_type == "fan":
        if state == "ON":
            card.classes(remove='border-gray-600', add='border-yellow-400 shadow-lg shadow-yellow-500/50')
            lbl.text = 'ON'
            lbl.classes(remove='text-gray-400', add='text-yellow-400')
            elements['icon'].classes(remove='text-gray-500', add='text-yellow-400') # Đổi màu icon
        else:
            card.classes(remove='border-yellow-400 shadow-lg shadow-yellow-500/50', add='border-gray-600')
            lbl.text = 'OFF'
            lbl.classes(remove='text-yellow-400', add='text-gray-400')
            elements['icon'].classes(remove='text-yellow-400', add='text-gray-500')

    elif d_type == "curtain":
        # Map state OPEN/CLOSE sang hiển thị MỞ/ĐÓNG
        display_text = "MỞ" if state == "OPEN" else "ĐÓNG"
        if state == "OPEN":
            card.classes(remove='border-gray-600', add='border-blue-400 shadow-lg shadow-blue-500/50')
            lbl.text = display_text
            lbl.classes(remove='text-gray-400', add='text-blue-400')
        else:
            card.classes(remove='border-blue-400 shadow-lg shadow-blue-500/50', add='border-gray-600')
            lbl.text = display_text
            lbl.classes(remove='text-blue-400', add='text-gray-400')

    elif d_type == "door":
        display_text = "Mở" if state == "OPEN" else "ĐÓNG"
        if state == "OPEN":
            card.classes(remove='border-gray-600', add='border-green-400 shadow-lg shadow-green-500/50')
            lbl.text = display_text
            lbl.classes(remove='text-gray-400', add='text-green-400')
            elements['icon'].classes(remove='text-gray-500', add='text-green-400')
        else:
            card.classes(remove='border-green-400 shadow-lg shadow-green-500/50', add='border-gray-600')
            lbl.text = display_text
            lbl.classes(remove='text-green-400', add='text-gray-400')
            elements['icon'].classes(remove='text-green-400', add='text-gray-500')

def add_log(text):
    container = ui_refs.get('log_container')
    log_area = ui_refs.get('log_area')
    client = getattr(container, 'client', None) or getattr(container, '_client', None)
    if not container or not log_area or not client:
        return

    async def _append():
        try:
            with container:
                ui.label(f"> {text}").classes('text-green-400 font-mono text-sm')
            log_area.scroll_to(percent=1.0)
        except RuntimeError:
            # Client có thể đã đóng; bỏ qua log
            return

    ui.run(_append(), client=client)

# Chạy app
if __name__ in {"__main__", "__mp_main__"}:
    init_interface()
    ui.run(title='Smart Home Pro', port=8080)
