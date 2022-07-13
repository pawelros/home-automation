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
  // inverse on/off logic
  const uint8_t OFF  = 1;
  const uint8_t ON   = 0;
  const uint8_t FLIP = 2;
}

// Child ID declaration of relays
const uint8_t KUCHNIA_OSWIETLENIE_WYSPA       = 1;
const uint8_t KUCHNIA_OSWIETLENIE_TUBY        = 2;
const uint8_t JADALNIA_OSWIETLENIE            = 3;
const uint8_t SALON_ZYRANDOL                  = 4;
const uint8_t BIURO_OSWIETLENIE_L1            = 5;
const uint8_t BIURO_OSWIETLENIE_L2            = 6;
const uint8_t PRZEDPOKOJ_OSWIETLENIE          = 7;
const uint8_t BALKON_OSWIETLENIE              = 8;
const uint8_t PODDASZE_OSWIETLENIE            = 9;
const uint8_t SYPIALNIA_OSWIETLENIE           = 10;
const uint8_t STASIU_OSWIETLENIE_L1           = 11;
const uint8_t STASIU_OSWIETLENIE_L2           = 12;

const uint8_t TEST_INPUT           = 50;


// Vector contaning child ID, description, output pin
std::vector<CustomSensor> customSensors = std::vector<CustomSensor>() = {
  { CustomSensor(KUCHNIA_OSWIETLENIE_TUBY,        "Kuchnia oswietlenie tuby",            18) },
  { CustomSensor(KUCHNIA_OSWIETLENIE_WYSPA,       "Kuchnia oswietlenie wyspa",           19) },
  { CustomSensor(JADALNIA_OSWIETLENIE,            "Jadalnia oswietlenie",                20) },
  { CustomSensor(SALON_ZYRANDOL,                  "Salon zyrandol poziom 1",             21) },
  { CustomSensor(BIURO_OSWIETLENIE_L1,            "Biuro oswietlenie poziom 1",          22) },
  { CustomSensor(BIURO_OSWIETLENIE_L2,            "Biuro oswietlenie poziom 2",          23) },
  { CustomSensor(PRZEDPOKOJ_OSWIETLENIE,          "Przedpokoj oswietlenie",              24) },
  { CustomSensor(BALKON_OSWIETLENIE,              "Balkon oswietlenie",                  25) },
  { CustomSensor(PODDASZE_OSWIETLENIE,            "Poddasze oswietlenie",                26) },
  { CustomSensor(SYPIALNIA_OSWIETLENIE,           "Sypialnia oswietlenie",               27) },
  { CustomSensor(STASIU_OSWIETLENIE_L1,           "Stasiu oswietlenie poziom 1",         28) },
  { CustomSensor(TEST_INPUT,                      "TEST INPUT",         30) },
  { CustomSensor(STASIU_OSWIETLENIE_L2,           "Stasiu oswietlenie poziom 2",         29) }
};

// Pushbuttons declaration
// Remember that names should be consistent with main loop in gateway.ino
OneButton test(A1, true);
// OneButton balkon(30, true);
// OneButton poddasze(31, true);
// OneButton sypialnia(32, true);
// OneButton stasiu(33, true);
