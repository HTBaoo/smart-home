import joblib
import os

from config import settings

class NLUEngine:
    def __init__(self):
        if os.path.exists(settings.NLU_MODEL_PATH):
            self.model = joblib.load(settings.NLU_MODEL_PATH)
            self.vectorizer = joblib.load(settings.NLU_VECTORIZER_PATH)
            print("✅ NLU Engine (với nhận diện Vị Trí) đã sẵn sàng!")
        else:
            self.model = None

        # --- TỪ ĐIỂN VỊ TRÍ ---
        self.LOCATIONS = {
            "living_room": ["phòng khách", "nhà ngoài","phòng chính"],
            "bedroom": ["phòng ngủ", "giường ngủ", "phòng con", "phần ngủ"],
            "kitchen": ["nhà bếp", "phòng ăn", "bếp"],
            "bathroom": ["nhà tắm", "vệ sinh", "toilet"],
            "meeting_room":["sảnh", "cửa chính", "cửa ra vào"],
            "all": ["tất cả", "hết", "cả nhà", "toàn bộ"]
        }
        self.GREET = [
            "xin chào", "chào", "hello", "hi", "alo", "ê bot", 
            "chào bạn", "chào em", "này", "hey", "có đó không",
            "bot ơi", "dậy đi", "thức dậy", "nghe không"
        ]
    def _smart_split(self, text):
        """(Giữ nguyên hàm xử lý 'à không' và 'và' như bài trước)"""
        text = text.lower().strip()
        
        # 1. Xử lý "quay xe"
        correction_keywords = ["à không", "nhầm", "ý lộn", "à quên", "sai rồi"]
        for kw in correction_keywords:
            if kw in text:
                parts = text.split(kw)
                if len(parts) > 1: text = parts[-1].strip()

        # 2. Xử lý câu ghép
        connector_keywords = [" và ", " rồi ", " sau đó ", " với lại ", ","]
        commands = [text]
        for kw in connector_keywords:
            new_commands = []
            for cmd in commands:
                if kw in cmd: new_commands.extend(cmd.split(kw))
                else: new_commands.append(cmd)
            commands = new_commands
        
        return [c.strip() for c in commands if c.strip()]

    def _extract_slot(self, text):
        """Hàm tìm vị trí trong câu không phụ thuộc dấu"""
        found_location = "unknown" # Mặc định không rõ ở đâu
      
        for loc_code, keywords in self.LOCATIONS.items():
            for kw in keywords:
                if kw in text:
                    found_location = loc_code
                    break # Tìm thấy rồi thì thôi
            if found_location != "unknown":
                break
                
        return found_location

    def predict(self, text):
        
        #if not self.model: return []

        sub_sentences = self._smart_split(text)
        results = []

        for sub_text in sub_sentences:
            # 1. Đoán Intent (Hành động)

            is_greet = False
            for greet in self.GREET:
                # Kiểm tra chính xác hoặc từ mở đầu (ví dụ: "chào nhé")
                if sub_text == greet or sub_text.startswith(greet + " "):
                    results.append({
                        "intent": "greet",  # Gán cứng intent là greet
                        "location": None,
                        "text": sub_text,
                        "confidence": 1.0   # Tự tin tuyệt đối
                    })
                    print(f"   🔹 Rule-based: '{sub_text}' -> Intent: greet")
                    is_greet = True
                    break
                if is_greet:
                    continue
            if not self.model: continue
            text_vec = self.vectorizer.transform([sub_text])
            
            intent = self.model.predict(text_vec)[0]
            probs = self.model.predict_proba(text_vec)[0]
            confidence = max(probs)

            # 2. Trích xuất Slot (Vị trí)
            location = self._extract_slot(sub_text)

            if confidence > 0.15: 
                results.append({
                    "intent": intent, 
                    "location": location,
                    "text": sub_text
                })
                print(f"   🔹 Phân tích: '{sub_text}' -> Hành động: {intent} | Vị trí: {location}")
            
        return results
