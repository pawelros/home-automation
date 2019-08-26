/**
 * @file Automation.h
 * @author Grzegorz Krajewski
 *
 * Automation for buttons & sensors.
 *
 * @license GPL V2
 */

#pragma once

#include "../CustomSensor/CustomSensor.hpp"
#include "../Mapping/Mapping.hpp"

void setOutput(const uint8_t& sensorId, const uint8_t& cmd = Relay::FLIP) {
  CustomSensor sensor = CustomSensor::getSensorById(sensorId, customSensors);
  const uint8_t state = (cmd == Relay::FLIP) ? !loadState(sensor.id) : cmd;

  saveState(sensor.id, state);
  digitalWrite(sensor.pin, state);

  send(sensor.message.set(state));
}

void bathroomClick() {
  setOutput(BATHROOM_LED_ID);
  setOutput(BATHROOM_LIGHT_ID);
}
void bathroomLongClick() {
  setOutput(BATHROOM_LED_ID, Relay::OFF);
  setOutput(BATHROOM_LED_ID, Relay::OFF);
  setOutput(BATHROOM_FAN_1_ID, Relay::OFF);
  setOutput(BATHROOM_FAN_2_ID, Relay::OFF);
}
void bathroomDoubleClick() {
  setOutput(BATHROOM_LED_ID);
  setOutput(BATHROOM_LIGHT_ID);
  setOutput(BATHROOM_FAN_1_ID);
  setOutput(BATHROOM_FAN_2_ID);
}

void setupButtons() {
  // Setup the button.

  bathroom.attachClick(bathroomClick);
  bathroom.attachLongPressStop(bathroomLongClick);
  bathroom.attachDoubleClick(bathroomDoubleClick);
}
