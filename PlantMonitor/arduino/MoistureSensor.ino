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

  irrigationSystem();
  
}

void sendJson(int moisture, float temp, float humid)
{
  String output_msg = "{\"moisture\" : "  + String(moisture) + ", \"temperature\" : " + String(temp) + ", \"humidity\" : " + String(humid) + "}";
  Serial.println(output_msg);  
}

//Reads from serial to determine wheather irrigation should be turned on 
void irrigationSystem()
{
  if(Serial.available() > 0)
  {
    int serial = Serial.read() - '0'; // convert int to ASCII using char
    Serial.flush();
    //if serial recieved is 0 (off) or 1 (on)
    switch(serial)
    {
      case 0:
        digitalWrite(LED,LOW);
        LCD.clear();
        LCD.setCursor(0,0);
        while(Serial.available() > 0)
        {
          //read in whole char array after 0 bit is set
          //sent string from Rpi
          char string = Serial.read();
          LCD.print(string);
        }
        break;

        case 1:
        digitalWrite(LED,HIGH);
        LCD.clear();
        LCD.setCursor(0,0);
        while(Serial.available() > 0)
        {
          //read in whole char array after 0 bit is set
          //Sent string from Rpi
          char string = Serial.read();
          LCD.print(string);
        }
        break;

        
        default:
        //nothing
        break;
    }
  }

}
