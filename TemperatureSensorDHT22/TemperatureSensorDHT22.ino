/**
   PostHTTPClient.ino

    Created on: 21.11.2016

*/
#include <Esp.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>

#define SERVER_IP "ip:port"
#define DHTPIN 14     // Digital pin connected to the DHT sensor 
#define DHTTYPE    DHT22     // DHT 22 (AM2302)

#ifndef STASSID
#define STASSID "WIFINetwork"
#define STAPSK "WIFIPassword"
#endif

String name = "Name";

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // ESP.wdtEnable(0);
  Serial.begin(115200);

  dht.begin();

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.hostname(name + "-temp-sensor");
  WiFi.begin(STASSID, STAPSK);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // wait for WiFi connection
  if ((WiFi.status() == WL_CONNECTED)) {
    //read temperature and humidity
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(h) || isnan(t)) {
      Serial.println("Failed to read from DHT sensor!");
    } else {
      float tf = (t * 1.8) + 32; // convert from celcius to fahrenheit
      Serial.print("Temperature ");
      Serial.print(tf);
      Serial.println("F ");
      Serial.print("Humidity ");
      Serial.println(h);
      WiFiClientSecure client;
      HTTPClient http;

      client.setInsecure();

      Serial.print("[HTTP] begin...\n");
      http.begin(client, "https://" SERVER_IP "/sensor-status?name=" + name + "&temperature=" + String(tf) + "&humidity=" + String(h));  // HTTP
      http.addHeader("Content-Type", "application/json");

      Serial.print("[HTTP] PUT...\n");
      // start connection and send HTTP header and body
      // int httpCode = http.POST("{\"hello\":\"world\"}");
      int httpCode = http.PUT("");
      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] PUT... code: %d\n", httpCode);

        if (httpCode == HTTP_CODE_OK) {
          const String& payload = http.getString();
          Serial.println("received payload:\n<<");
          Serial.println(payload);
          Serial.println(">>");
        }
      } else {
        Serial.printf("[HTTP] PUT... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    }
  }

  delay(2000);
}
