int solenoidPin = 4;    //This is the output pin on the Arduino we are using
bool solOnOff = false;
int state = 1; //start in close position

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
  Serial.begin(9600);
  digitalWrite(flowsensor, HIGH); // Optional Internal Pull-Up
  attachInterrupt(digitalPinToInterrupt(flowsensor), flow, RISING); // Setup Interrupt
}
 
void loop() {

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
  if (state == 2
  ) {
    solOnOff = true;
    //Serial.println("Open");
    Serial.println(state);
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
