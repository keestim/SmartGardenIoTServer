#include <ArduinoJson.h>

/*
##########VALUES#############
          TEMP
temp values are relativly normal,study
area seems to be an average 22 degrees

          HUMIDITY
humidity value max has been recorded at 86
which has been measured after placing a wet
piece of tissue paper in front of it for 1 minute

         SOIL MOISTURE
Soil moisture sensor seems to be a max of 844
during submersion in glass of water and values
5-30 measured when nothing is touching it

############################
*/

#include <DHT.h>
#define DHTTYPE DHT11 //DHT library board type

#include <LiquidCrystal.h>
//LCD PINS#################
int rs = 9;
int enable =10;
int d4 = 2;
int d5 = 3;
int d6 = 4;
int d7 = 5;
//##########################
bool blinkLED = false;
int moistureSensor = A0;
int LED = 8;
int DHTPIN = A1; // DHT pin allocation *A1*

//DHT object taking pin number and board type in this case DHT11
DHT tempSens(DHTPIN, DHTTYPE);
//LCD object created 
LiquidCrystal LCD(rs, enable, d4, d5, d6, d7);

void setup() 
{
  Serial.begin(9600);
  
  pinMode(moistureSensor, INPUT);
  pinMode(LED,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  //Setup LCD
  LCD.begin(16,2);
  LCD.setCursor(0,0);

  //initalise tempSens
  tempSens.begin();
}

void loop()
{
  delay(500); //delay for temp and humid sensor very slow!!
  int m = analogRead(moistureSensor);
  float t = tempSens.readTemperature();
  float h = tempSens.readHumidity();

  sendJson(m,t,h);

  readSerialMsgs();
  acuateBlinkLed();
  
}

void sendJson(int moisture, float temp, float humid)
{
  String output_msg = "{\"moisture\" : "  + String(moisture) + ", \"temperature\" : " + String(temp) + ", \"humidity\" : " + String(humid) + "}";
  Serial.println(output_msg);  
}

//Reads from serial to determine wheather irrigation should be turned on 
void readSerialMsgs()
{
  String serialMsg;

  while(Serial.available()) {
    delay(3);
   
    if (Serial.available() > 0) {
      serialMsg += char(Serial.read());// read the incoming data as string
    }
  }

  // if the string that's been read in is longer that 0 length, then try to parse the string as JSON
  // all serial communication should occur through JSON
  if (serialMsg.length() > 0)
  {
    DynamicJsonDocument doc(200);    
    auto error = deserializeJson(doc, serialMsg);
    
    if (error) {
        Serial.print(F("deserializeJson() failed with code "));
        Serial.println(error.c_str());
        return;
    }

    if (doc.containsKey("blink_led"))
    {
      LCD.clear();
      LCD.setCursor(0,0);
      String serialMsg = "Water";
      LCD.print(serialMsg);
      
      String ledState = doc["blink_led"];
      blinkLED = (ledState == "true");
    }
  }
}

void acuateBlinkLed()
{  
  if (blinkLED)
  {
    for (int i = 0; i < 10; i++)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
      delay(100);
    }

    blinkLED = false;
  }
}
