import paho.mqtt.client as mqtt
from config import settings

class MqttController:
    def __init__(self):
        self.client = mqtt.Client()
        try:
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
            print(f"✅ MQTT OK")
        except:
            print("❌ Lỗi MQTT")

    def send_command(self, location, device, action):
        """
        location: living_room, bedroom...
        device: light, fan, curtain...
        action: on, off
        """
        # Tạo topic động: home/phong_khach/den
        # 1. Chuẩn hóa lệnh (Gemini trả về 'turn_on', ta chỉ gửi 'on')
        payload = action.replace("turn_", "").replace("_curtain", "") 
        # Kết quả payload sẽ là: 'on', 'off', 'open', 'close'
        topic = f"home/{location}/{device}"
        
        self.client.publish(topic, action)
        print(f"📡 Gửi MQTT: {topic} -> {payload}")