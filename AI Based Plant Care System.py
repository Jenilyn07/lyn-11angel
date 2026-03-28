#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

#define DHTPIN D4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* serverName = "http://YOUR_PC_IP:5000/data";

int soilMoisturePin = A0;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  dht.begin();

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting...");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int soilMoisture = analogRead(soilMoisturePin);

    // Dummy values for pH & NPK (replace with real sensors)
    float pH = 7.5;
    int nitrogen = 20;
    int phosphorus = 15;
    int potassium = 10;

    String url = serverName + "?temp=" + temperature +
                 "&hum=" + humidity +
                 "&soil=" + soilMoisture +
                 "&ph=" + pH +
                 "&n=" + nitrogen +
                 "&p=" + phosphorus +
                 "&k=" + potassium;

    http.begin(url);
    int httpCode = http.GET();

    Serial.println(httpCode);
    http.end();
  }

  delay(5000);
}
from flask import Flask, request, jsonify

app = Flask(__name__)

def analyze_data(temp, hum, soil, ph, n, p, k):
    alerts = []

    # Soil Moisture
    if soil < 300:
        alerts.append("Soil is too dry. Water the plant.")
    elif soil > 800:
        alerts.append("Soil is too wet. Reduce watering.")

    # Temperature
    if temp > 35:
        alerts.append("Temperature too high. Move to shade.")
    elif temp < 15:
        alerts.append("Temperature too low.")

    # Humidity
    if hum < 30:
        alerts.append("Humidity is low. Spray water.")

    # pH
    if ph > 7:
        alerts.append("Soil is alkaline.")
    elif ph < 6:
        alerts.append("Soil is acidic.")

    # NPK
    if n < 10:
        alerts.append("Low Nitrogen. Add fertilizer.")
    if p < 10:
        alerts.append("Low Phosphorus.")
    if k < 10:
        alerts.append("Low Potassium.")

    return alerts


@app.route('/data', methods=['GET'])
def receive_data():
    temp = float(request.args.get('temp'))
    hum = float(request.args.get('hum'))
    soil = int(request.args.get('soil'))
    ph = float(request.args.get('ph'))
    n = int(request.args.get('n'))
    p = int(request.args.get('p'))
    k = int(request.args.get('k'))

    result = analyze_data(temp, hum, soil, ph, n, p, k)

    return jsonify({"alerts": result})


if __name__ == '__main__':
    app.run(debug=True)
<!DOCTYPE html>
<html>
<head>
    <title>Plant Care System</title>
</head>
<body>
    <h1>Plant Health Monitor</h1>
    <div id="output"></div>

    <script>
        async function getData() {
            let res = await fetch("http://localhost:5000/data?temp=30&hum=40&soil=200&ph=7.5&n=5&p=8&k=6");
            let data = await res.json();

            document.getElementById("output").innerHTML =
                data.alerts.join("<br>");
        }

        setInterval(getData, 5000);
    </script>
</body>
</html>
