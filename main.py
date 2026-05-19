#include <WiFi.h>
#include <WebServer.h>

// Настройки Wi-Fi
const char* ssid = "Wokwi-GUEST";     // Wokwi Wi-Fi
const char* password = "";             // Без пароля для Wokwi

// Настройка веб-сервера
WebServer server(80);

// Пин светодиода (встроенный LED на ESP32)
const int ledPin = 2;  // GPIO2

// Переменные для состояния
bool ledState = false;
int brightness = 128;  // яркость от 0 до 255

// HTML страница с интерфейсом
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
    <title>Умная лампочка</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f0f0f0;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            max-width: 400px;
            margin: auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        button {
            padding: 15px 30px;
            font-size: 18px;
            margin: 10px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            transition: 0.3s;
        }
        .on-btn {
            background-color: #4CAF50;
            color: white;
        }
        .off-btn {
            background-color: #f44336;
            color: white;
        }
        .on-btn:hover { background-color: #45a049; }
        .off-btn:hover { background-color: #da190b; }
        .brightness-control {
            margin: 20px;
        }
        input {
            width: 80%;
            padding: 10px;
            margin: 10px;
        }
        .status {
            font-size: 20px;
            margin: 20px;
            padding: 10px;
            border-radius: 5px;
        }
        .on-status { background-color: #d4ffd4; color: #2e7d32; }
        .off-status { background-color: #ffd4d4; color: #c62828; }
    </style>
</head>
<body>
    <div class="container">
        <h1>💡 Умная лампочка</h1>
        <div id="status" class="status">---</div>
        
        <div>
            <button class="on-btn" onclick="sendCommand('on')">Включить</button>
            <button class="off-btn" onclick="sendCommand('off')">Выключить</button>
        </div>
        
        <div class="brightness-control">
            <h3>Яркость: <span id="brightnessValue">0</span>%</h3>
            <input type="range" min="0" max="100" value="50" id="brightnessSlider" onchange="setBrightness()">
        </div>
    </div>

    <script>
        function updateStatus() {
            fetch('/state')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.state === 'on') {
                        statusDiv.innerHTML = '✅ Лампочка ВКЛЮЧЕНА';
                        statusDiv.className = 'status on-status';
                    } else {
                        statusDiv.innerHTML = '❌ Лампочка ВЫКЛЮЧЕНА';
                        statusDiv.className = 'status off-status';
                    }
                    document.getElementById('brightnessSlider').value = data.brightness;
                    document.getElementById('brightnessValue').innerText = data.brightness;
                });
        }

        function sendCommand(cmd) {
            fetch('/' + cmd)
                .then(() => updateStatus());
        }

        function setBrightness() {
            const value = document.getElementById('brightnessSlider').value;
            document.getElementById('brightnessValue').innerText = value;
            fetch('/brightness?value=' + value)
                .then(() => updateStatus());
        }

        updateStatus();
        setInterval(updateStatus, 1000);
    </script>
</body>
</html>
)rawliteral";

// Функция для установки яркости с помощью ШИМ
void setBrightnessValue(int percent) {
    brightness = map(percent, 0, 100, 0, 255);
    if (ledState) {
        analogWrite(ledPin, brightness);
    }
}

// Обработчики команд
void handleRoot() {
    server.send(200, "text/html", index_html);
}

void handleOn() {
    ledState = true;
    analogWrite(ledPin, brightness);
    server.send(200, "text/plain", "OK");
}

void handleOff() {
    ledState = false;
    analogWrite(ledPin, 0);
    server.send(200, "text/plain", "OK");
}

void handleBrightness() {
    if (server.hasArg("value")) {
        int percent = server.arg("value").toInt();
        percent = constrain(percent, 0, 100);
        setBrightnessValue(percent);
    }
    server.send(200, "text/plain", "OK");
}

void handleState() {
    String json = "{\"state\":\"" + String(ledState ? "on" : "off") + 
                  "\",\"brightness\":" + String(map(brightness, 0, 255, 0, 100)) + "}";
    server.send(200, "application/json", json);
}

void setup() {
    Serial.begin(115200);
    pinMode(ledPin, OUTPUT);
    analogWrite(ledPin, 0);
    
    // Подключение к Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Подключение к Wi-Fi");
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    
    Serial.println("\nWi-Fi подключен!");
    Serial.print("IP адрес: ");
    Serial.println(WiFi.localIP());
    
    // Настройка маршрутов веб-сервера
    server.on("/", handleRoot);
    server.on("/on", handleOn);
    server.on("/off", handleOff);
    server.on("/brightness", handleBrightness);
    server.on("/state", handleState);
    
    server.begin();
    Serial.println("Веб-сервер запущен");
}

void loop() {
    server.handleClient();
}
