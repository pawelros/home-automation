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
const uint8_t KUCHNIA_OSWIETLENIE_TUBY        = 79;
const uint8_t KUCHNIA_OSWIETLENIE_WYSPA       = 26;
const uint8_t PODDASZE_OSWIETLENIE            = 78;
const uint8_t SYPIALNIA_OSWIETLENIE           = 71;
const uint8_t BIURO_OSWIETLENIE_L1            = 68;
const uint8_t BIURO_OSWIETLENIE_L2            = 67;
const uint8_t LAZIENKA_DOL_OSWIETLENIE_LUSTRA = 62;
const uint8_t LAZIENKA_GORA_OSWIETLENIE       = 59;
const uint8_t SALON_OSWIETLENIE_SZYNA_1_L1    = 41;
const uint8_t SALON_OSWIETLENIE_SZYNA_1_L2    = 40;
const uint8_t SALON_OSWIETLENIE_SZYNA_2_L1    = 24;
const uint8_t SALON_OSWIETLENIE_SZYNA_2_L2    = 23;
const uint8_t SALON_ZYRANDOL_L1               = 36;
const uint8_t SALON_ZYRANDOL_L2               = 35;
const uint8_t BALKON_OSWIETLENIE              = 37;
const uint8_t JADALNIA_OSWIETLENIE            = 32;
const uint8_t PRZEDPOKOJ_OSWIETLENIE          = 30;

// Vector contaning child ID, description, output pin
std::vector<CustomSensor> customSensors = std::vector<CustomSensor>() = {
  { CustomSensor(KUCHNIA_OSWIETLENIE_TUBY,        "Kuchnia oswietlenie tuby",            24) },
  { CustomSensor(KUCHNIA_OSWIETLENIE_WYSPA,       "Kuchnia oswietlenie wyspa",           25) },
  { CustomSensor(PODDASZE_OSWIETLENIE,            "Poddasze oswietlenie",                26) },
  { CustomSensor(SYPIALNIA_OSWIETLENIE,           "Sypialnia oswietlenie",               27) },
  { CustomSensor(BIURO_OSWIETLENIE_L1,            "Biuro oswietlenie poziom 1",          28) },
  { CustomSensor(BIURO_OSWIETLENIE_L2,            "Biuro oswietlenie poziom 2",          29) },
  { CustomSensor(LAZIENKA_GORA_OSWIETLENIE,       "Lazienka gora oswietlenie",           30) },
  { CustomSensor(LAZIENKA_DOL_OSWIETLENIE_LUSTRA, "Lazienka dol oswietlenie lustra",     31) },
  { CustomSensor(SALON_OSWIETLENIE_SZYNA_1_L1,    "Szalon oswietlenie szyna 1 poziom 1", 33) },
  { CustomSensor(SALON_OSWIETLENIE_SZYNA_1_L2,    "Szalon oswietlenie szyna 1 poziom 2", 34) },
  { CustomSensor(SALON_OSWIETLENIE_SZYNA_2_L1,    "Szalon oswietlenie szyna 2 poziom 1", 35) },
  { CustomSensor(SALON_OSWIETLENIE_SZYNA_2_L2,    "Szalon oswietlenie szyna 2 poziom 2", 36) },
  { CustomSensor(SALON_ZYRANDOL_L1,               "Salon zyrandol poziom 1",             37) },
  { CustomSensor(SALON_ZYRANDOL_L2,               "Salon zyrandol poziom 2",             38) },
  { CustomSensor(BALKON_OSWIETLENIE,              "Balkon oswietlenie",                  39) },
  { CustomSensor(JADALNIA_OSWIETLENIE,            "Jadalnia oswietlenie",                40) },
  { CustomSensor(PRZEDPOKOJ_OSWIETLENIE,          "Przedpokoj oswietlenie",              41) },
};

// Pushbuttons declaration
// Remember that names should be consistent with main loop in gateway.ino
OneButton kuchnia(A1, true);
OneButton sypialnia(A2, true);
OneButton biuro(A3, true);
OneButton lazienkaDol(A4, true);
OneButton salon(A5, true);
OneButton przedpokoj(A6, true);
OneButton lazienkaGora(A7, true);
