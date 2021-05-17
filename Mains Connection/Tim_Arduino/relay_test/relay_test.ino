#include <ArduinoJson.h>
//code from :https://www.instructables.com/How-to-Use-Water-Flow-Sensor-Arduino-Tutorial/

const int relayPin = 10;
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
  // put your setup code here, to run once:
  
  pinMode(relayPin, OUTPUT);
  pinMode(sensorPin, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(sensorPin, HIGH);
  initialiseFlowMeter();
}

void acuateBlinkLed()
{
  Serial.write("BLINK LED");
  
  if (blinkLED)
  {
    for (int i = 0; i < 10; i++)
    {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(500);
      digitalWrite(LED_BUILTIN, LOW);
      delay(500);
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
  
  // The Hall-effect sensor is connected to pin 2 which uses interrupt 0.
  // Configured to trigger on a FALLING state change (transition from HIGH
  // state to LOW state)
  attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
}

void readFlowMeter(){
  // only record is valve is open
  //when valve is closed, reset water measurement, etc!
  if((millis() - oldTime) > 1000)    // Only process counters once per second
  { 
    // Disable the interrupt while calculating flow rate and sending the value to
    // the host
    detachInterrupt(sensorInterrupt);
        
    // Because this loop may not complete in exactly 1 second intervals we calculate
    // the number of milliseconds that have passed since the last execution and use
    // that to scale the output. We also apply the calibrationFactor to scale the output
    // based on the number of pulses per second per units of measure (litres/minute in
    // this case) coming from the sensor.
    flowRate = ((1000.0 / (millis() - oldTime)) * pulseCount) / calibrationFactor;
    
    // Note the time this processing pass was executed. Note that because we've
    // disabled interrupts the millis() function won't actually be incrementing right
    // at this point, but it will still return the value it was set to just before
    // interrupts went away.
    oldTime = millis();
    
    // Divide the flow rate in litres/minute by 60 to determine how many litres have
    // passed through the sensor in this 1 second interval, then multiply by 1000 to
    // convert to millilitres.
    flowMilliLitres = (flowRate / 60) * 1000;
    
    // Add the millilitres passed in this second to the cumulative total
    totalMilliLitres += flowMilliLitres;
      
    unsigned int frac;

    // Reset the pulse counter so we can start incrementing again
    pulseCount = 0;
    
    // Enable the interrupt again now that we've finished sending output
    attachInterrupt(sensorInterrupt, pulseCounter, FALLING);
  }
}

//when every 0.5 seconds quickly close and open valve, to prevent any over pour issues, etc
void loop() 
{
  readSerialMsgs();
  
  if (valveOpen)
  {
    readFlowMeter();
    digitalWrite(relayPin, HIGH);
  } 
  else {
    totalMilliLitres = 0;
    digitalWrite(relayPin, LOW);
  }  
  
  String waterVolumeJSON = "{\"total_volume\" : " + String(totalMilliLitres) + ", \"pump_state\" : " + String(valveOpen) + "}\n";
  Serial.print(waterVolumeJSON);

  acuateBlinkLed();
  delay(500);
}

void readSerialMsgs()
{
  String serialMsg;
  
  // put your main code here, to run repeatedly:

  while(Serial.available()) {
    delay(3);
    Serial.print("Reading MSG");
    
    if (Serial.available() > 0) {
      serialMsg += char(Serial.read());// read the incoming data as string
    }
  }

  if (serialMsg.length() > 0)
  {
    DynamicJsonDocument doc(200);
    Serial.print(serialMsg);
    Serial.println("");
    
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


/*
Insterrupt Service Routine
 */
void pulseCounter()
{
  // Increment the pulse counter
  pulseCount++;
}
