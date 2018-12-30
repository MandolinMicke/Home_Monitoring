#include <dht.h>

dht DHT;


#define DHT11_PIN 7
#define SENDER_ID 16679936
void setup(){
  Serial.begin(9600);
  pinMode(13,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if (Serial.available()>0) {
      String data = Serial.readString();
      if (data == "temperature") {
        int chk = DHT.read11(DHT11_PIN);
        Serial.println(DHT.temperature);
      } else if (data == "humidity") {
        int chk = DHT.read11(DHT11_PIN);
        Serial.println(DHT.humidity);
      }
      delay(3);
      
      // Serial.println("Look what I got: " + data);
      //digitalWrite(13,false);
  } else {
    //Serial.println("ready");
    //delay();
  }

  
  
  // int chk = DHT.read11(DHT11_PIN);
 
  //Serial.println(DHT.temperature);
 
  //Serial.println(DHT.humidity);
  
}
