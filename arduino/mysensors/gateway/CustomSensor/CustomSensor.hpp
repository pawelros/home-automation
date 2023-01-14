/**
 * @file CustomSensor.h
 * @author Grzegorz Krajewski
 *
 * Representation of Custom Sensor class.
 *
 * @license GPL V2
 */


#pragma once

#include <MySensors.h>


class CustomSensor {
public:
  CustomSensor(const uint8_t& _id, const char* _desc, const uint8_t& _pin) {
    id = _id;
    description = _desc;
    pin = _pin;
    message = MyMessage(id, V_LIGHT);
  }

template <size_t N>
  static CustomSensor getSensorById(const uint8_t& sensorId, const CustomSensor (&sensors)[N]) {
    for (CustomSensor sensor : sensors) {
      if (sensor.id == sensorId) return sensor;
    }

    return CustomSensor(0, "UNKNOWN", 0);
  }

  uint8_t id;
  const char* description;
  uint8_t pin;
  MyMessage message;
};