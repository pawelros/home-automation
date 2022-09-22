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
const uint8_t LAZIENKA_DOL_OSWIETL            = 13;
const uint8_t LAZIENKA_DOL_SW_LUSTRO          = 14;
const uint8_t LAZIENKA_GORA_SW                = 15;
const uint8_t WENTYLATOR_LAZIENKA_WC          = 17;
const uint8_t WENTYLATOR_LAZIENKA_PRYSZNIC    = 18;
const uint8_t PIEC                            = 19;
const uint8_t LAZIENKA_DOL_OGRZ_LUSTRO        = 20;



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
  { CustomSensor(STASIU_OSWIETLENIE_L2,           "Stasiu oswietlenie poziom 2",         29) },
  { CustomSensor(LAZIENKA_DOL_OSWIETL,            "Łazienka dół oświetlenie",            30) },
  { CustomSensor(LAZIENKA_DOL_SW_LUSTRO,          "Łazienka dół światło lustro",         31) },
  { CustomSensor(LAZIENKA_GORA_SW,                "Łazienka góra światło",               32) },
  { CustomSensor(WENTYLATOR_LAZIENKA_WC,          "Wentylator łazienka WC",              34) },
  { CustomSensor(WENTYLATOR_LAZIENKA_PRYSZNIC,    "Wentylator łazienka Prysznic",        35) },
  { CustomSensor(PIEC,                            "Piec gazowy ogrzewanie",              36) },
  { CustomSensor(LAZIENKA_DOL_OGRZ_LUSTRO,        "Łazienka dół ogrzewanie lustro",      37) }
};

// Pushbuttons declaration
// Remember that names should be consistent with main loop in gateway.ino
OneButton przedpokoj_drzwi(A1, true);
// OneButton balkon(30, true);
// OneButton poddasze(31, true);
// OneButton sypialnia(32, true);
// OneButton stasiu(33, true);
