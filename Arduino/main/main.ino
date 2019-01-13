#include <dht.h>

dht DHT;




// needed for room temp/humid sensor
#define DHT11_PIN 7

// needed for pipe temp sensor
float tempC;
int reading;
int tempPin = 0; // Analog

// parameters needed for nexa controls
int trans_pin = 12;

unsigned long controller_id = 21474946;
int kPulseHigh = 275;
int kPulseLow0 = 275;
int kPulseLow1 = 1225;

int kLowPulseLength = 64;
int* low_pulse_array;
int kControllerIdOffset = 0;
int kControllerIdLength = 26;
int kGroupFlagOffset = 26;
int kOnFlagOffset = 27;
int kDeviceIdOffset = 28;
int kDeviceIdLength = 4;
int kDimOffset = 32;
int kDimLength = 4;

int delaybetween = 150;
int trials = 5;
int radiator = 0;
int heatcord = 1;
int extra = 2;

void setup(){
  Serial.begin(9600);
  pinMode(trans_pin, OUTPUT);
  low_pulse_array = (int*)calloc((kLowPulseLength + (2 * kDimLength)), sizeof(int));
  analogReference(INTERNAL);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  if (Serial.available()>0) {
      String data = Serial.readString();
      if (data == "roomtemperature") {
        int chk = DHT.read11(DHT11_PIN);
        Serial.println(DHT.temperature);
        
      } else if (data == "pipetemperature") {
        float temp = pipeTemp();
        Serial.println(temp);
        
      } else if (data == "humidity") {
        int chk = DHT.read11(DHT11_PIN);
        Serial.println(DHT.humidity);
        
      } else if (data == "radiator_on") {
        TurnOn(controller_id,radiator);
        Serial.println("radiator on");
        
      } else if (data == "radiator_off") {
        TurnOff(controller_id,radiator);
        Serial.println("radiator off");
        
      } else if (data == "heatcord_on") {
        TurnOn(controller_id,heatcord);
        Serial.println("heatcord_on");
        
      } else if (data == "heatcord_off") {
        TurnOff(controller_id,heatcord);
        Serial.println("heatcord_off");
        
      } else if (data == "extra_on") {
        TurnOn(controller_id,extra);
        Serial.println("extra_on");
        
      } else if (data == "extra_off") {
        TurnOff(controller_id,extra);
        Serial.println("extra_off");
        
      } else {
        Serial.println(data);
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




void TurnOn(unsigned long controller_id, unsigned int device_id)
{
    SetControllerBits(controller_id);
    SetBit(kGroupFlagOffset, 0);
    SetBit(kOnFlagOffset, 1);
    SetDeviceBits(device_id);
    for (int i=0; i<trials; i++) {
      Transmit(kLowPulseLength);
      delay(delaybetween);
    }
}

void TurnOff(unsigned long controller_id, unsigned int device_id)
{
    SetControllerBits(controller_id);
    SetBit(kGroupFlagOffset, 0);
    SetBit(kOnFlagOffset, 0);
    SetDeviceBits(device_id);
    for (int i=0; i<trials; i++) {
      Transmit(kLowPulseLength);
      delay(delaybetween);
    }
}

void SetDeviceBits(unsigned int device_id)
{
    bool device[kDeviceIdLength];
    unsigned long ldevice_id = device_id;
    itob(device, ldevice_id, kDeviceIdLength);
    int bit;
    for (bit=0; bit < kDeviceIdLength; bit++) {
        SetBit(kDeviceIdOffset+bit, device[bit]);
    }
}

void SetControllerBits(unsigned long controller_id)
{
    bool controller[kControllerIdLength];
    itob(controller, controller_id, kControllerIdLength);

    int bit;
    for (bit=0; bit < kControllerIdLength; bit++) {
        SetBit(kControllerIdOffset+bit, controller[bit]);
    }
}

void SetBit(unsigned int bit_index, bool value)
{
    // Each actual bit of data is encoded as two bits on the wire...
    if (!value) {
        // Data 0 = Wire 01
        low_pulse_array[(bit_index*2)] = kPulseLow0;
        low_pulse_array[(bit_index*2) + 1] = kPulseLow1;
    } else {
        // Data 1 = Wire 10
        low_pulse_array[(bit_index*2)] = kPulseLow1;
        low_pulse_array[(bit_index*2) + 1] = kPulseLow0;
    }
}

void Transmit(int pulse_length)
{
    int pulse_count;
    int transmit_count;

    cli(); // disable interupts

    for (transmit_count = 0; transmit_count < 2; transmit_count++)
    {
        TransmitLatch1();
        TransmitLatch2();

        /*
         * Transmit the actual message
         * every wire bit starts with the same short high pulse, followed
         * by a short or long low pulse from an array of low pulse lengths
         */
        for (pulse_count = 0; pulse_count < pulse_length; pulse_count++)
        {
            digitalWrite(trans_pin, HIGH);
            delayMicroseconds(kPulseHigh);
            digitalWrite(trans_pin, LOW);
            delayMicroseconds(low_pulse_array[pulse_count]);
        }

        TransmitLatch2();

        delayMicroseconds(10000);
    }

    sei(); // enable interupts
}

void TransmitLatch1(void)
{
    // bit of radio shouting before we start
    digitalWrite(trans_pin, HIGH);
    delayMicroseconds(kPulseLow0);
    // low for 9900 for latch 1
    digitalWrite(trans_pin, LOW);
    delayMicroseconds(9900);
}

void TransmitLatch2(void)
{
    // high for a moment 275
    digitalWrite(trans_pin, HIGH);
    delayMicroseconds(kPulseLow0);
    // low for 2675 for latch 2
    digitalWrite(trans_pin, LOW);
    delayMicroseconds(2675);
}

void itob(bool *bits, unsigned long integer, int length) {
    for (int i=0; i<length; i++){
        if ((integer / power2(length-1-i))==1){
            integer-=power2(length-1-i);
            bits[i]=1;
        }
        else bits[i]=0;
    }
}

unsigned long power2(int power){    //gives 2 to the (power)
    return (unsigned long) 1 << power;
}


float pipeTemp() {
  reading = analogRead(tempPin);
  tempC = reading/9.31;
  return tempC;
  
}

