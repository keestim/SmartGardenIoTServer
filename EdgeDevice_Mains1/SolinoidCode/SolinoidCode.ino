int solenoidPin = 4;    //This is the output pin on the Arduino we are using
bool solOnOff = false;
int state = 1; //start in close position
int LED = 7; // led pin
int counter = 0; //counter gets set to 20 to blink the LED 10 times

// FLOWRATE
  volatile int flow_frequency; // Measures flow sensor pulses
  // Calculated litres/hour
  float vol = 0.0,l_minute;
  unsigned char flowsensor = 2; // Sensor Input
  int skipflow = 0;
  
  void flow () // Interrupt function
  {
   flow_frequency++;
  }

void setup() {
  // put your setup code here, to run once:
  pinMode(solenoidPin, OUTPUT);           //Sets the pin as an output
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  digitalWrite(flowsensor, HIGH); // Optional Internal Pull-Up
  attachInterrupt(digitalPinToInterrupt(flowsensor), flow, RISING); // Setup Interrupt
  digitalWrite(LED, LOW);
}
 
void loop() {
<<<<<<< Updated upstream:EdgeDevice_Mains1/SolinoidCode/SolinoidCode.ino
 Serial.println(counter);
=======
  
 // --------------------------------------------------------- \\
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
 // --------------------------------------------------------- \\

>>>>>>> Stashed changes:Mains Connection/SolinoidCode/SolinoidCode.ino
if (skipflow < 1)
   {
  if(flow_frequency != 0)
  {
      // Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
      l_minute = (flow_frequency / 1); // (Pulse frequency x 60 min) / 7.5Q = flowrate in L/hour
      Serial.print(flow_frequency);
      Serial.print(" ");
      flow_frequency = 0; // Reset Counter

    }
    else 
    {
      Serial.print("0");
      Serial.print(" ");
      //Serial.println(" flow rate = 0 ");
    }
}

  int temp = Serial.parseInt();
  
  if (!(temp == NULL))
  {
    state = temp;
  }
  
  if (state == 1) {
    solOnOff = false;
    //Serial.println("Closed");
    Serial.println(state);
    }
  if (state == 2) 
    {
    solOnOff = true;
    //Serial.println("Open");
    Serial.println(state);
    }
    if (state == 3) 
    {
    counter = 10;
    state = 0;
    }

    if (counter > 0)
    {
      counter--;
      digitalWrite(LED, HIGH);
      delay(1000);
      digitalWrite(LED, LOW);
    }
  
  if (solOnOff == true)
  {
  digitalWrite(solenoidPin, HIGH);    //Switch Solenoid ON
  delay(1000);   
  }
  else
  {
  digitalWrite(solenoidPin, LOW);     //Switch Solenoid OFF
  delay(1000);      
  }
}

// Read Serial messages
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
// Read Serial messages

void acuateBlinkLed()
{
  Serial.write("BLINK LED");
  
  if (blinkLED)
  {
    for (int i = 0; i < 10; i++)
    {
      digitalWrite(LED, HIGH);
      delay(100);
      digitalWrite(LED, LOW);
      delay(100);
    }

    blinkLED = false;
  }
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
