#include <ArduinoJson.h>
//code from :https://www.instructables.com/How-to-Use-Water-Flow-Sensor-Arduino-Tutorial/

const int redLed = 12;
const int greenLed = 11;
const int buzzer = 10;
const int smokeA0 = A5;
// Your threshold value
const int sensorThres = 400;
bool blinkLED = false;

void setup() {
  Serial.begin(9600);

  pinMode(redLed, OUTPUT);
  pinMode(greenLed, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(smokeA0, INPUT);
}

void loop() {
  readSerialMsgs();

  int smokeValue = int(analogRead(smokeA0));
  
  // Checks if it has reached the threshold value
  if (int(smokeValue) > 400)
  {
    digitalWrite(redLed, HIGH);
    digitalWrite(greenLed, LOW);
    tone(buzzer, 1000, 200);
  }
  else
  {
    digitalWrite(redLed, LOW);
    digitalWrite(greenLed, HIGH);
    noTone(buzzer);
  }
  
  String smokeDataJSON = "{\"smoke_reading\" : " + String(smokeValue) + "}\n";
  Serial.print(smokeDataJSON);

  acuateBlinkLed();
  delay(500);
}

void acuateBlinkLed()
{  
  if(blinkLED)
  {
    for (int i = 0; i < 10; i++)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(100);
      digitalWrite(LED_BUILTIN, LOW);
      delay(100);
    }
  }
}


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
      String ledState = doc["blink_led"];
      blinkLED = (ledState == "true");
    }
  }
}
