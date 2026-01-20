import asyncio
import websockets
import threading
import queue
import wave
import os

class ESP32Mic:
    def __init__(self, port=5000, save_path="temp_voice.wav"):
        self.port = port
        self.save_path = save_path
        self.audio_queue = queue.Queue()
        self.audio_buffer = bytearray()
        self.is_recording = False
        self.client_ws = None 
        self.loop = None
        
        # Chạy server luồng riêng
        self.server_thread = threading.Thread(target=self._start_server_thread, daemon=True)
        self.server_thread.start()
        print(f"🎤 [ESP32Mic] Server đang khởi động tại port {port}...")

    def _start_server_thread(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.loop = new_loop 

        async def run_server():
            print(f"✅ WebSocket Server (Mic) listening on 0.0.0.0:{self.port}")
            # Tắt Ping/Timeout
            async with websockets.serve(
                self._handler, "0.0.0.0", self.port, 
                ping_interval=None, ping_timeout=None
            ):
                await asyncio.Future() 

        try:
            new_loop.run_until_complete(run_server())
        except Exception as e:
            print(f"❌ [ESP32Mic] Server Crash: {e}")
        finally:
            new_loop.close()

    async def _handler(self, websocket):
        print(f"🔗 [ESP32Mic] Kết nối mới: {websocket.remote_address}")
        self.client_ws = websocket 
        try:
            async for message in websocket:
                if isinstance(message, str):
                    if message == "WAKE":
                        print("🎙️ [ESP32] Bắt đầu thu âm...")
                        self.is_recording = True
                        self.audio_buffer = bytearray()
                    elif message == "MIC_OFF":
                        self.is_recording = False
                        if len(self.audio_buffer) > 0:
                            await self._save_to_file_async()
                            self.audio_queue.put(self.save_path)
                            self.audio_buffer = bytearray()
                elif isinstance(message, bytes):
                    if self.is_recording:
                        self.audio_buffer.extend(message)
        except: pass 
        finally:
            if self.is_recording and len(self.audio_buffer) > 1000:
                print("⚠️ [ESP32] Mất kết nối! Đang lưu dữ liệu...")
                self.is_recording = False
                await self._save_to_file_async()
                self.audio_queue.put(self.save_path)
                self.audio_buffer = bytearray()
            self.client_ws = None
            print("❌ [ESP32Mic] Đã đóng kết nối")

    async def _save_to_file_async(self):
        await asyncio.to_thread(self._write_wav)

    def _write_wav(self):
        try:
            with wave.open(self.save_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 16-bit
                wf.setframerate(16000)
                wf.writeframes(self.audio_buffer)
        except: pass

    def listen(self):
        return self.audio_queue.get(block=True)

    def send_command(self, command_text):
        if self.client_ws and self.loop:
            asyncio.run_coroutine_threadsafe(self.client_ws.send(command_text), self.loop)

    # === QUAN TRỌNG: GỬI STREAMING (CHIA NHỎ GÓI TIN) ===
    def send_audio(self, audio_data):
        if self.client_ws and self.loop and self.loop.is_running():
            try:
                # Chia nhỏ mỗi gói 1024 bytes
                CHUNK_SIZE = 1024
                async def send_chunks():
                    for i in range(0, len(audio_data), CHUNK_SIZE):
                        chunk = audio_data[i : i + CHUNK_SIZE]
                        await self.client_ws.send(chunk)
                        await asyncio.sleep(0.005) # Nghỉ 5ms để ESP32 kịp thở
                    print(f"✅ Đã gửi xong {len(audio_data)} bytes.")

                asyncio.run_coroutine_threadsafe(send_chunks(), self.loop)
            except Exception as e:
                print(f"❌ Lỗi gửi âm thanh: {e}")
        else:
            print("⚠️ Chưa kết nối ESP32, không thể phát loa.")