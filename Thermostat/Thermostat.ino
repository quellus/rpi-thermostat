#include <Esp.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Arduino_JSON.h>

#define SERVER_IP "192.168.68.203:8000"

#ifndef STASSID
#define STASSID "Oof"
#define STAPSK "NoOneKnowsThePassword"
#endif

int pumpPin = 13;
int fanPin = 12;
int acPin = 5;
int furnacePin = 4;


void setup() {
  Serial.begin(115200);

  pinMode(pumpPin, OUTPUT);
  pinMode(fanPin, OUTPUT);
  pinMode(acPin, OUTPUT);
  pinMode(furnacePin, OUTPUT);

  Serial.println();
  Serial.println();
  Serial.println();

  WiFi.hostname("Thermostat");
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
    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    http.begin(client, "http://" SERVER_IP "/?is_from_thermostat=true");  // HTTP
    http.addHeader("Content-Type", "application/json");

    Serial.print("[HTTP] GET...\n");
    // start connection and send HTTP header and body
    // int httpCode = http.POST("{\"hello\":\"world\"}");
    int httpCode = http.GET();
    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);

      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        const String& payload = http.getString();
        Serial.println("received payload:\n<<");
        Serial.println(payload);
        JSONVar jsonData = JSON.parse(payload);
        JSONVar pins = jsonData["status"]["pins"];
        Serial.println(pins);
        if (JSON.stringify(pins["pump"]) == "true") {
          digitalWrite(pumpPin, HIGH);
        } else {
          digitalWrite(pumpPin, LOW);
        }
        if (JSON.stringify(pins["fan_on"]) == "true") {
          digitalWrite(fanPin, HIGH);
        } else {
          digitalWrite(fanPin, LOW);
        }
        if (JSON.stringify(pins["ac"]) == "true") {
          digitalWrite(acPin, HIGH);
        } else {
          digitalWrite(acPin, LOW);
        }
        if (JSON.stringify(pins["furnace"]) == "true") {
          digitalWrite(furnacePin, HIGH);
        } else {
          digitalWrite(furnacePin, LOW);
        }
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }

  delay(2000);
}
