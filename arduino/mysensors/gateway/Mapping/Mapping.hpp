/**
 * @file Mapping.h
 * @author Grzegorz Krajewski
 *
 * Mappings.
 *
 * @license GPL V2
 */

#pragma once

#include <OneButton.h>
#include "../CustomSensor/CustomSensor.hpp"

namespace Relay {
  const uint8_t OFF  = 0;
  const uint8_t ON   = 1;
  const uint8_t FLIP = 2;
}

// Child ID declaration of relays
const uint8_t SERVER_ROOM_ID       = 1;
const uint8_t BATHROOM_LED_ID      = 2;
const uint8_t BATHROOM_LIGHT_ID    = 3;
const uint8_t BATHROOM_FAN_1_ID    = 4;
const uint8_t BATHROOM_FAN_2_ID    = 5;

// Vector contaning child ID, description, output pin
std::vector<CustomSensor> customSensors = std::vector<CustomSensor>() = {
  { CustomSensor(SERVER_ROOM_ID,    "Serwerownia",    24) },
  { CustomSensor(BATHROOM_LED_ID,     "Lazienka LED",       25) },
  { CustomSensor(BATHROOM_LIGHT_ID,   "Lazienka Halogeny",       26) },
  { CustomSensor(BATHROOM_FAN_1_ID,   "Wentylator Prysznic",       27) },
  { CustomSensor(BATHROOM_FAN_2_ID,   "Wentylator Lazienka",       28) },
};

// Pushbuttons declaration
// Remember that names should be consistent with main loop in gateway.ino
// OneButton serverRoom(A1, true);
OneButton bathroom(A2, true);
