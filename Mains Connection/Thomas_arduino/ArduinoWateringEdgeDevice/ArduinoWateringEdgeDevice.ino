#include <ArduinoJson.h>
//code from :https://www.instructables.com/How-to-Use-Water-Flow-Sensor-Arduino-Tutorial/

int solenoidPin = 4;
bool valveOpen = false;
bool blinkLED = false;

byte sensorInterrupt = 0;  // 0 = digital pin 2
byte sensorPin       = 2;

// The hall-effect flow sensor outputs approximately 4.5 pulses per second per
// litre/minute of flow.
float calibrationFactor = 4.5;

volatile byte pulseCount;  

float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;

unsigned long oldTime;

void setup() {
    // Initialize a serial connection for reporting values to the host
  Serial.begin(9600);

pinMode(solenoidPin, OUTPUT);
  pinMode(sensorPin, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(sensorPin, HIGH);
  
  initialiseFlowMeter();
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

void initialiseFlowMeter()
{
  pulseCount        = 0;
  flowRate          = 0.0;
  flowMilliLitres   = 0;
  totalMilliLitres  = 0;
  oldTime           = 0;
  
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

void readFlowMeter(){

  if((millis() - oldTime) > 1000)    
  { 

    detachInterrupt(sensorInterrupt);
        

    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / calibrationFactor;
    
    oldTime = millis();
    
    flowMilliLitres = (flowRate / 60) * 1000;
  
    totalMilliLitres += flowMilliLitres;
      
    unsigned int frac;

    // Reset pulse 
    pulseCount = 0;
    
    // Enable the interrupt again now that we've finished sending output
    attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  }
}

void loop() 
{
  readSerialMsgs();
  
  if (valveOpen)
  {
    readFlowMeter();
  digitalWrite(solenoidPin, HIGH);
  } 
  else {
    totalMilliLitres = 0;
  digitalWrite(solenoidPin, LOW);
  }  
  
  String waterVolumeJSON = "{\"total_volume\" : " + String(totalMilliLitres) + ", \"pump_state\" : " + String(valveOpen) + "}\n";
  Serial.print(waterVolumeJSON);

  acuateBlinkLed();
  delay(500);
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

  if (serialMsg.length() > 0)
  {
    DynamicJsonDocument doc(200);    
    auto error = deserializeJson(doc, serialMsg);
    
    if (error) {
        Serial.print(F("deserializeJson() failed with code "));
        Serial.println(error.c_str());
        return;
    }

    if (doc.containsKey("valve_state"))
    {
      String valveState = doc["valve_state"];

      valveOpen = (valveState == "open");
    }

    if (doc.containsKey("blink_led"))
    {
      String ledState = doc["blink_led"];
      blinkLED = (ledState == "true");
    }
  }
}


void pulseCounter()
{
  // Increment the pulse counter
  pulseCount++;
}
