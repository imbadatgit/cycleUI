#include <DigiCDC.h>

#define LED 1
#define BUTTON 2

// controller state
int prevState = HIGH;
unsigned long prevTime;
unsigned long cycles = 0;
unsigned long delta = 0;
boolean moving = false;

// cycling state
int revolutions = 0;
unsigned long rideTime;

void setup() {
  SerialUSB.begin();
  pinMode(BUTTON, INPUT);
  pinMode(LED, OUTPUT);
  
  prevTime = millis();
}


// sends time delta, ride time and revolutions through usb
void sendSerial() {
  SerialUSB.print("d=");
  SerialUSB.println(delta);
  SerialUSB.print("t=");
  SerialUSB.println(rideTime);
  SerialUSB.print("v=");
  SerialUSB.println(revolutions);
}


void loop() {
  // read in the current button state
  int sensorVal = digitalRead(BUTTON);

  // check for state change
  if (sensorVal != prevState) {
    if (sensorVal == HIGH) { // contact closed --> revolution done
    
      revolutions++;
      unsigned long currTime = millis();
      
      // set start time?
      if (!moving) {
        moving = true;
        prevTime = currTime;
      }

      // calculate time delta
      // NOTE: currTime will overflow after 50 days
      delta = currTime - prevTime;
      prevTime = currTime;
      rideTime += delta;

      sendSerial();
    }

    prevState = sensorVal;
  }
  
  
  cycles++;
  
  // do USB communication every 100 CPU cycles
  if (cycles > 100) {
    cycles = 0;
    unsigned long current = millis();
    unsigned long ldelta = current - prevTime;


    // check whether we're idle
    if (ldelta > 3000) {
      delta = 0.0;
      sendSerial();
      moving = false;
    }
  }
  
  // revolutions are slow, so delay next measure
  SerialUSB.delay(10);
}
