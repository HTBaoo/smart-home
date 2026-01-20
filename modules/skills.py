import datetime
import webbrowser
import requests
import random

class SkillEngine:
    def get_time(self):
        """Lấy giờ hiện tại"""
        now = datetime.datetime.now()
        return now.strftime("%H giờ %M phút")
    
    def get_date(self):
        """Lấy ngày tháng hiện tại (Có xử lý thứ tiếng Việt)"""
        now = datetime.datetime.now()
        # Mapping thứ tiếng Anh sang Việt
        days = {
            0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm", 
            4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"
        }
        weekday = days[now.weekday()]
        return f"Hôm nay là {weekday}, ngày {now.day} tháng {now.month} năm {now.year}"

    def play_music(self):
        """Mở nhạc trên máy tính (Youtube)"""
        # Link nhạc Lofi chill
        music_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk" 
        try:
            webbrowser.open(music_url)
            return "Đã mở nhạc thư giãn cho bạn trên máy tính."
        except:
            return "Xin lỗi, tôi không mở được trình duyệt."

    def get_weather(self):
        """Lấy thời tiết (Cần API Key)"""
        # --- CÁCH 1: GIẢ LẬP (Nếu chưa có API Key dùng cái này cho nhanh) ---
        # return "Hôm nay trời nắng đẹp, nhiệt độ khoảng 28 độ C"

        # --- CÁCH 2: DÙNG OPENWEATHERMAP (Khuyên dùng) ---
        try:
            # 1. Đăng ký free tại: openweathermap.org để lấy API Key
            api_key = "f0bec10053e82b3f042589b590d11414" # <--- DÁN KEY CỦA BẠN VÀO ĐÂY
            city = "Da Nang" # Hoặc "Ho Chi Minh", "Da Nang"
            url = (
                f"http://api.openweathermap.org/data/2.5/forecast?"
                f"lat=16.072157&lon=108.221587&appid={api_key}"
                f"&units=metric&lang=vi&cnt=1" 
            )
            
            # Gửi yêu cầu
            response = requests.get(url, timeout=5).json()
            
            # Kiểm tra lỗi
            if response.get("cod") != "200": # API Forecast trả về chuỗi "200"
                print(f"❌ Lỗi API: {response.get('message')}")
                return "Không lấy được dữ liệu thời tiết."

            # --- CÁCH ĐỌC DỮ LIỆU CỦA API FORECAST ---
            # API này trả về một danh sách 'list', ta lấy phần tử đầu tiên [0]
            current_data = response['list'][0]
            
            temp = int(current_data["main"]["temp"])          # Nhiệt độ
            desc = current_data["weather"][0]["description"]  # Mô tả
            hum = current_data["main"]["humidity"]            # Độ ẩm
            wind = current_data["wind"]["speed"]              # Gió
            pop = int(current_data.get("pop", 0) * 100)       # Tỉ lệ mưa (Probability of Precipitation)

            # Tạo câu trả lời thông minh hơn (có thêm tỉ lệ mưa)
            msg = f"Dự báo tại chỗ bạn, {desc} , nhiệt độ khoảng {temp} độ , độ ẩm trong khoảng {hum} phần trăm."
            
            if pop > 50:
                msg += f" Lưu ý, khả năng mưa là {pop} phần trăm."
            
            return msg
            
        except Exception as e:
            print(f"❌ Lỗi kết nối Weather: {e}")
            return "Tôi bị mất kết nối với đài khí tượng rồi."