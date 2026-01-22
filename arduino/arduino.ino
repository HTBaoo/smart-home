#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include "driver/i2s.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// ================= CẤU HÌNH MẠNG =================
#define WIFI_SSID ""      // Tên Wifi
#define WIFI_PASS ""   // Mật khẩu
const char *WS_SERVER_IP = ""; // IP máy tính Python
const int WS_PORT = 5000;

// ================= CẤU HÌNH ÂM THANH =============
#define SAMPLE_RATE 16000
#define WAKE_THRESHOLD    4000  
#define SILENCE_THRESHOLD 800   
#define MIC_GAIN          2     
#define SILENCE_DURATION  1500  

// CHÂN KẾT NỐI
#define I2S_SPEAKER_PORT I2S_NUM_0
#define SPK_BCK 26
#define SPK_LRC 25
#define SPK_DIN 22

#define I2S_MIC_PORT I2S_NUM_1
#define MIC_BCK 27
#define MIC_WS  14
#define MIC_SD  34

#define LED_GREEN 13 
#define LED_RED   12 

WebSocketsClient webSocket;
int32_t mic_raw[512]; 
int16_t mic_pcm[512];

bool isPlaying = false;      
bool isRecording = false;    
unsigned long lastSilenceTime = 0;
unsigned long lastAudioPacketTime = 0; 

// ================= KHỞI TẠO DRIVER ================
void setupDrivers() {
  // 1. CẤU HÌNH LOA (Buffer LỚN để nghe mượt)
  i2s_config_t spk_cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 16,    // Tăng lên 16 (quan trọng!)
    .dma_buf_len = 128,     // Tăng lên 128 (quan trọng!)
    .use_apll = false, .tx_desc_auto_clear = true, .fixed_mclk = 0
  };
  i2s_pin_config_t spk_pin = { .mck_io_num = I2S_PIN_NO_CHANGE, .bck_io_num = SPK_BCK, .ws_io_num = SPK_LRC, .data_out_num = SPK_DIN, .data_in_num = I2S_PIN_NO_CHANGE };
  i2s_driver_install(I2S_SPEAKER_PORT, &spk_cfg, 0, NULL);
  i2s_set_pin(I2S_SPEAKER_PORT, &spk_pin);
  i2s_set_clk(I2S_SPEAKER_PORT, SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT, I2S_CHANNEL_MONO);

  // 2. CẤU HÌNH MIC
  i2s_config_t mic_cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8, .dma_buf_len = 64,
    .use_apll = false, .tx_desc_auto_clear = false, .fixed_mclk = 0
  };
  i2s_pin_config_t mic_pin = { .mck_io_num = I2S_PIN_NO_CHANGE, .bck_io_num = MIC_BCK, .ws_io_num = MIC_WS, .data_out_num = I2S_PIN_NO_CHANGE, .data_in_num = MIC_SD };
  i2s_driver_install(I2S_MIC_PORT, &mic_cfg, 0, NULL);
  i2s_set_pin(I2S_MIC_PORT, &mic_pin);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_CONNECTED:
      Serial.println("[WS] DA KET NOI!");
      digitalWrite(LED_GREEN, HIGH); delay(200); digitalWrite(LED_GREEN, LOW);
      break;
    case WStype_DISCONNECTED:
      Serial.println("[WS] MAT KET NOI!");
      digitalWrite(LED_RED, HIGH); 
      break;
    case WStype_BIN: {
      // Python gửi âm thanh xuống -> Phát loa
      if (!isPlaying) {
        Serial.println(">>> LOA DANG NOI...");
        isPlaying = true; 
        isRecording = false; 
        digitalWrite(LED_RED, HIGH); 
        digitalWrite(LED_GREEN, LOW);
      }
      size_t written;
      i2s_write(I2S_SPEAKER_PORT, payload, length, &written, portMAX_DELAY);
      lastAudioPacketTime = millis();
      break;
    }
  }
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); // Chống sập nguồn
  Serial.begin(115200);
  pinMode(LED_GREEN, OUTPUT); pinMode(LED_RED, OUTPUT);

  WiFi.setTxPower(WIFI_POWER_11dBm); // Giảm công suất Wifi để tiết kiệm điện
  Serial.print("Dang noi WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println(" OK!");

  setupDrivers();

  webSocket.begin(WS_SERVER_IP, WS_PORT, "/");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(3000);
}

void loop() {
  webSocket.loop(); 

  // --- LOGIC 1: ĐANG PHÁT LOA ---
  if (isPlaying) {
     size_t temp;
     i2s_read(I2S_MIC_PORT, mic_raw, sizeof(mic_raw), &temp, 0); // Xả buffer mic

     // Chờ 1000ms không có dữ liệu mới coi là nói xong
     if (millis() - lastAudioPacketTime > 1000) {
        Serial.println("<<< LOA XONG -> MO LAI MIC");
        isPlaying = false;
        digitalWrite(LED_RED, LOW);
        digitalWrite(LED_GREEN, HIGH);
     }
  }
  // --- LOGIC 2: THU ÂM ---
  else { 
    size_t bytes_read = 0;
    i2s_read(I2S_MIC_PORT, mic_raw, sizeof(mic_raw), &bytes_read, 0);

    if (bytes_read > 0) {
      int samples = bytes_read / 4;
      long current_vol = 0;

      for (int i=0; i<samples; i++) {
        int32_t s = mic_raw[i] >> 14; 
        s *= MIC_GAIN;
        if (s > 32767) s = 32767; else if (s < -32768) s = -32768;
        mic_pcm[i] = (int16_t)s;
        current_vol += abs(s);
      }
      current_vol /= samples;

      if (!isRecording) {
        if (current_vol > WAKE_THRESHOLD) {
          Serial.printf("💥 BUM! (Vol: %d)\n", current_vol);
          webSocket.sendTXT("WAKE"); 
          isRecording = true;
          lastSilenceTime = millis();
          digitalWrite(LED_GREEN, LOW);
          digitalWrite(LED_RED, HIGH);
        }
      } 
      else {
        webSocket.sendBIN((uint8_t*)mic_pcm, samples * 2);
        
        if (current_vol < SILENCE_THRESHOLD) {
          if (millis() - lastSilenceTime > SILENCE_DURATION) {
            Serial.println("💤 Im lang -> Ngung gui");
            webSocket.sendTXT("MIC_OFF"); 
            isRecording = false;
            digitalWrite(LED_GREEN, LOW);
            digitalWrite(LED_RED, LOW);
          }
        } else {
          lastSilenceTime = millis(); 
        }
      }
    }
  }
  delay(1); 
}