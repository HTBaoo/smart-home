import socket
import speech_recognition as sr
import wave
import struct
import os

# Cấu hình mạng (Giống trong ESP8266)
UDP_IP = "0.0.0.0" # Lắng nghe tất cả các IP
UDP_PORT = 12345

# Cấu hình âm thanh
SAMPLE_RATE = 8000
DURATION = 5  # Thời gian thu âm mỗi lần (giây)
TEMP_FILENAME = "temp_audio.wav"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Đang lắng nghe âm thanh từ ESP8266 tại cổng {UDP_PORT}...")

r = sr.Recognizer()

while True:
    frames = []
    print("Đang thu âm... (Nói đi bạn!)")
    
    # Thu thập dữ liệu trong vòng DURATION giây
    for _ in range(int(SAMPLE_RATE * DURATION)):
        data, addr = sock.recvfrom(1024) # Nhận 1 byte từ ESP
        # Dữ liệu từ ESP là 1 byte int (0-255), cần đóng gói lại
        val = int.from_bytes(data, byteorder='little')
        
        # Mở rộng lại biên độ để to hơn (tùy chỉnh)
        frames.append(struct.pack('B', val)) 
        
    print("Đang xử lý chuyển đổi Speech-to-Text...")

    # Lưu thành file WAV
    wf = wave.open(TEMP_FILENAME, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(1) # 1 byte (8 bits)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Gửi file WAV lên Google để dịch
    try:
        with sr.AudioFile(TEMP_FILENAME) as source:
            audio_data = r.record(source)
            # lang='vi-VN' để nhận diện tiếng Việt
            text = r.recognize_google(audio_data, language="vi-VN") 
            print(f"--> KẾT QUẢ: {text}")
    except sr.UnknownValueError:
        print("--> Không nghe rõ (Quá ồn hoặc mic kém)")
    except sr.RequestError as e:
        print(f"--> Lỗi kết nối Google: {e}")
    except Exception as e:
        print(f"Lỗi: {e}")