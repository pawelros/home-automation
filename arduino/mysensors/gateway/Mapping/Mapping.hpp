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
const uint8_t KUCHNIA_OSWIETLENIE_TUBY        = 1;
const uint8_t KUCHNIA_OSWIETLENIE_WYSPA       = 2;
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


// Vector contaning child ID, description, output pin
std::vector<CustomSensor> customSensors = std::vector<CustomSensor>() = {
  { CustomSensor(KUCHNIA_OSWIETLENIE_TUBY,        "Kuchnia oswietlenie tuby",            1) },
  { CustomSensor(KUCHNIA_OSWIETLENIE_WYSPA,       "Kuchnia oswietlenie wyspa",           2) },
  { CustomSensor(JADALNIA_OSWIETLENIE,            "Jadalnia oswietlenie",                3) },
  { CustomSensor(SALON_ZYRANDOL,                  "Salon zyrandol poziom 1",             4) },
  { CustomSensor(BIURO_OSWIETLENIE_L1,            "Biuro oswietlenie poziom 1",          22) },
  { CustomSensor(BIURO_OSWIETLENIE_L2,            "Biuro oswietlenie poziom 2",          6) },
  { CustomSensor(PRZEDPOKOJ_OSWIETLENIE,          "Przedpokoj oswietlenie",              7) },
  { CustomSensor(BALKON_OSWIETLENIE,              "Balkon oswietlenie",                  8) },
  { CustomSensor(PODDASZE_OSWIETLENIE,            "Poddasze oswietlenie",                9) },
  { CustomSensor(SYPIALNIA_OSWIETLENIE,           "Sypialnia oswietlenie",               10) },
  { CustomSensor(STASIU_OSWIETLENIE_L1,           "Stasiu oswietlenie poziom 1",         11) },
  { CustomSensor(STASIU_OSWIETLENIE_L2,           "Stasiu oswietlenie poziom 2",         12) }
};

// Pushbuttons declaration
// Remember that names should be consistent with main loop in gateway.ino
OneButton kuchnia(26, true);
OneButton jadalnia(26, true);
OneButton salon(27, true);
OneButton biuro(28, true);
OneButton przedpokoj(29, true);
OneButton balkon(30, true);
OneButton poddasze(31, true);
OneButton sypialnia(32, true);
OneButton stasiu(33, true);
