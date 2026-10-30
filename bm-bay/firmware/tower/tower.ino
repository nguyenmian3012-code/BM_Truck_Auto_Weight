// Đèn cột Bình Minh. Chỉ cắm nguồn 24V. WiFi, không dây tín hiệu.
// Nguồn 24V vào buck 5V nuôi ESP32. Bốn relay đóng ngắt đèn đỏ, vàng, xanh và còi 24V.
// Chân dưới đây là chân IN của module relay. Mất mạng quá 2 giây thì tắt hết.

#include <WiFi.h>

const char* WIFI_SSID = "sua-ten-wifi";
const char* WIFI_PASS = "sua-mat-khau";
const char* SCALE_HOST = "192.168.1.50";
const uint16_t SCALE_PORT = 8770;

const int PIN_RED = 25;
const int PIN_YELLOW = 26;
const int PIN_GREEN = 27;
const int PIN_HORN = 14;
const bool RELAY_ON = HIGH;

unsigned long lastOk = 0;

void setLamp(int pin, bool on) {
  digitalWrite(pin, on ? RELAY_ON : !RELAY_ON);
}

void allOff() {
  setLamp(PIN_RED, false);
  setLamp(PIN_YELLOW, false);
  setLamp(PIN_GREEN, false);
  setLamp(PIN_HORN, false);
}

bool flag(const String& body, const char* key) {
  String needle = String("\"") + key + "\":true";
  return body.indexOf(needle) >= 0;
}

void apply(const String& body) {
  setLamp(PIN_RED, flag(body, "red"));
  setLamp(PIN_YELLOW, flag(body, "yellow"));
  setLamp(PIN_GREEN, flag(body, "green"));
  setLamp(PIN_HORN, flag(body, "horn"));
  lastOk = millis();
}

void poll() {
  WiFiClient client;
  if (!client.connect(SCALE_HOST, SCALE_PORT)) return;
  client.print("GET /tower HTTP/1.0\r\nHost: ");
  client.print(SCALE_HOST);
  client.print("\r\nConnection: close\r\n\r\n");
  String body;
  unsigned long start = millis();
  while (client.connected() && millis() - start < 800) {
    while (client.available()) body += (char)client.read();
  }
  client.stop();
  int mark = body.indexOf("\r\n\r\n");
  if (mark < 0) return;
  body = body.substring(mark + 4);
  if (body.indexOf("{") < 0) return;
  apply(body);
}

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_HORN, OUTPUT);
  allOff();
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) poll();
  if (lastOk == 0 || millis() - lastOk > 2000) allOff();
  delay(200);
}
