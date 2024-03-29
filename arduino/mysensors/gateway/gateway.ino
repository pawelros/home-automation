/**
 * @file gateway.ino
 * @author Grzegorz Krajewski
 *
 * Implementation of the MySensors Gateway.
 *
 * @license GPL V2
 */

// Enable serial gateway
#define MY_GATEWAY_SERIAL

// Define a lower baud rate for Arduino's running on 8 MHz (Arduino Pro Mini 3.3V & SenseBender)
#if F_CPU == 16000000L
#define MY_BAUD_RATE 115200 // 3840
#endif

// Remember to add library to Arduino path
//#include <ArduinoSTL.h>
#include <MySensors.h>
#include "./CustomSensor/CustomSensor.hpp"
#include "./Mapping/Mapping.hpp"
#include "./Automation/Automation.hpp"

void before() {
  for (const CustomSensor sensor : customSensors) {
    const uint8_t pin = sensor.pin;
    pinMode(pin, OUTPUT);

    uint8_t currentState = loadState(sensor.id);
    // Check whether EEPROM cell was used before
    if (currentState == 0xFF) {
      currentState = Relay::ON;
      saveState(sensor.id, currentState);
    }
    digitalWrite(pin, !currentState);
  }
}

void setup() {
  setupButtons();
}

void presentation()
{
  // Send the sketch version information to the gateway and Controller
  sendSketchInfo("Gateway", "1.2");

  // Send actual states
  for (CustomSensor sensor : customSensors) {
    const uint8_t id = sensor.id;
    present(id, S_LIGHT, sensor.description);
    uint8_t state = loadState(id);

    send(sensor.message.set(state));
  }
}

void loop() {
  przedpokoj_drzwi.tick();
  // Keep sensing buttons
   kuchnia.tick();
   jadalnia.tick();
   salon.tick();
   biuro.tick();
  // przedpokoj.tick();
   balkon.tick();
   poddasze.tick();
   sypialnia.tick();
   stasiu.tick();
}

void receive(const MyMessage &message) {
  // We only expect one type of message from controller. But we better check anyway.
  if (message.type==V_LIGHT) {
    CustomSensor sensor = CustomSensor::getSensorById(message.sensor, customSensors);
    const bool value = message.getBool();
    // Store state in eeprom
    saveState(sensor.id, value);
    // Change relay state
    digitalWrite(sensor.pin, !value);
    // Send ACK
    send(sensor.message.set(value));
  }
}
