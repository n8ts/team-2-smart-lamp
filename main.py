#define BLYNK_PRINT Serial

/* Fill in information from Blynk Device Info here */
#define BLYNK_TEMPLATE_ID "TMPL6ECP1E1nc"
#define BLYNK_TEMPLATE_NAME "Home automation"
#define BLYNK_AUTH_TOKEN "AO4j4Og9mWl4i6JzsYotUMR5yW_avBtA"

/* here is the All necessery library*/
#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>
#include <LiquidCrystal.h>

// Your WiFi credentials.
// Set password to "" for open networks.
char ssid[] = "Wokwi-GUEST";
char pass[] = "";

const int rs = 4, en = 5, d4 = 18, d5 = 19, d6 = 21, d7 = 22;  //pin numbers of the lcd display
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);                     //object of the lcd display

WidgetLED led1(V1);           //widget for led on blynk dashbord
WidgetLED led2(V3);           //widget for led on blynk dashbord
WidgetTerminal terminal(V0);  //widget for terminal box on blynk dashbord

bool st_1 = false;     // state for button press led1
bool mode_st = false;  // state for button press mode
bool st = false;       // state for button press led2

bool read_data;
int last_val = 0;  //detecting for change lux value

BLYNK_CONNECTED() {
  Blynk.syncVirtual(V3);
  Blynk.syncVirtual(V2);
  Blynk.syncVirtual(V4);
  Blynk.syncVirtual(V5);
}

BLYNK_WRITE(V2)  // switch control for load 2
{
  mode_st = param.asInt();

  if (mode_st) {
    terminal.println("Automatic Mode");
    lcd.setCursor(0, 0);
    lcd.print("Automatic Mode");  //display the sensor data
    lcd.setCursor(0, 1);          //position of the text on display
    lcd.print("                        ");
  }
}
BLYNK_WRITE(V4)  // switch control for load 1
{
  if (mode_st == false)
    st = param.asInt();
}
BLYNK_WRITE(V5)  // switch control for load 2
{
  if (mode_st == false)
    st_1 = param.asInt();
}

/* Function for configuration the connected device */
void setup() {
  Serial.begin(115200);                       //confegering the boud rate
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);  //confegering the blynk
  pinMode(12, OUTPUT);                        //LED pin confeguration
  pinMode(14, OUTPUT);                        //LED pin confeguration
  pinMode(2, INPUT_PULLUP);                   //button pin confeguration
  pinMode(23, INPUT_PULLUP);                  //button pin confeguration
  pinMode(15, INPUT_PULLUP);                  //button pin confeguration
  lcd.begin(16, 2);                           //confegering the lcd display size
}

//main loop
void loop() {
  Blynk.run();             //run blynk main function
  int a = analogRead(34);  //taking reading from LDR sensor

  int b = map(a, 32, 4063, 0, 255);  //converted sensor data into 0 to 255 value


  int e = digitalRead(15);  //taking reading from mode button

  if (e == 0) {
    mode_st = !mode_st;
    Blynk.virtualWrite(V2, mode_st);
    delay(100);
  }
  
  if (mode_st) {
    if (last_val != b) {          //if sensor value change
      analogWrite(12, b);         //change brightness of led acording the sensor value
      analogWrite(14, b);         //change brightness of led acording the sensor value
      Blynk.virtualWrite(V1, b);  //change brightness of blynk dashboard led acording the sensor value
      Blynk.virtualWrite(V3, b);
      terminal.print("Automatic Mode Light LUX:");  //display the reading on the blynk iot dashboad
      terminal.println(map(a, 32, 4058, 100, 0));   //display the reading on the blynk iot dashboad percentages of light lux
      lcd.setCursor(0, 0);
      lcd.print("Automatic Mode");  //display the sensor data
      lcd.setCursor(0, 1);                          //position of the text on display
      lcd.print("Light LUX: ");                     //display the sensor data
      lcd.print(map(a, 32, 4058, 100, 0));          //display the sensor percentage
      lcd.print("%    ");                              //display the unite of the sensor
    }
  }
  while (mode_st == false) {

    int c = digitalRead(2);   //taking reading from button 1
    int d = digitalRead(23);  //taking reading from button 2
    lcd.setCursor(0, 0);      //position of the text on display
    lcd.print("Manually:       ");
    if (c == 0) {
      st = !st;
      Blynk.virtualWrite(V4, st);
      delay(10);
    }
    if (d == 0) {
      st_1 = !st_1;
      Blynk.virtualWrite(V5, st_1);
      delay(10);
    }

    if (digitalRead(15) == 0 && mode_st==false) {
      lcd.setCursor(0, 0);
      lcd.print("Automatic Mode");
      lcd.setCursor(0, 1);  //position of the text on display
      lcd.print("                 ");
      mode_st = true;
      delay(100);
      break;
    }
    if (st) {
      lcd.setCursor(0, 1);  //position of the text on display
      lcd.print("LED1 ON ");
      analogWrite(12, 255);
      Blynk.virtualWrite(V1, 255);
    }

    else {
      lcd.setCursor(0, 1);  //position of the text on display
      lcd.print("LED1 OFF");
      analogWrite(12, 0);
      Blynk.virtualWrite(V1, 0);
    }
    if (st_1) {
      lcd.setCursor(8, 1);  //position of the text on display
      lcd.print("LED2 ON ");
      analogWrite(14, 255);
      Blynk.virtualWrite(V3, 255);
    } else {
      lcd.setCursor(8, 1);  //position of the text on display
      lcd.print("LED2 OFF");
      analogWrite(14, 0);
      Blynk.virtualWrite(V3, 0);
    }
  }
  last_val = b;  //recorded the previous sensor data
  delay(100);    // this speeds up the simulation
}
