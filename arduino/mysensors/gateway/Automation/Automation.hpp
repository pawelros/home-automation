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
  digitalWrite(sensor.pin, !state);

  send(sensor.message.set(state));
}

void balkonClick() {
  setOutput(BALKON_OSWIETLENIE);
}

void kuchniaClick() {
  setOutput(KUCHNIA_OSWIETLENIE_TUBY);
  setOutput(KUCHNIA_OSWIETLENIE_WYSPA);
}

void kuchniaLongClick() {
  setOutput(KUCHNIA_OSWIETLENIE_WYSPA, 0);
  setOutput(KUCHNIA_OSWIETLENIE_TUBY, 0);
}

void kuchniaDoubleClick() {
  setOutput(KUCHNIA_OSWIETLENIE_WYSPA, 1);
  setOutput(KUCHNIA_OSWIETLENIE_TUBY, 0);
}

void jadalniaClick() {
  setOutput(JADALNIA_OSWIETLENIE);
}

void salonClick() {
  setOutput(SALON_ZYRANDOL);
}

void biuroClick() {
  setOutput(BIURO_OSWIETLENIE_L1);
}

void biuroLongClick() {
  setOutput(BIURO_OSWIETLENIE_L1, 0);
  setOutput(BIURO_OSWIETLENIE_L2, 0);
}

void biuroDoubleClick() {
  setOutput(BIURO_OSWIETLENIE_L2);
}

void przedpokojClick() {
  setOutput(PRZEDPOKOJ_OSWIETLENIE);
}

void poddaszeClick() {
  setOutput(PODDASZE_OSWIETLENIE);
}

void sypialniaClick() {
  setOutput(SYPIALNIA_OSWIETLENIE);
}

void stasiuClick() {
  setOutput(STASIU_OSWIETLENIE_L1);
}

void stasiuLongClick() {
  setOutput(STASIU_OSWIETLENIE_L1, 0);
  setOutput(STASIU_OSWIETLENIE_L2, 0);
}

void stasiuDoubleClick() {
  setOutput(STASIU_OSWIETLENIE_L2);
}

void przedpokoj_drzwiClick() {
  setOutput(PRZEDPOKOJ_OSWIETLENIE);
}

void setupButtons() {
  // Setup the button.

  balkon.attachClick(balkonClick);

  przedpokoj_drzwi.attachClick(przedpokoj_drzwiClick);
  kuchnia.attachClick(kuchniaClick);
  kuchnia.attachLongPressStop(kuchniaLongClick);
  kuchnia.attachDoubleClick(kuchniaDoubleClick);

  jadalnia.attachClick(jadalniaClick);

  salon.attachClick(salonClick);

  biuro.attachClick(biuroClick);
  biuro.attachLongPressStop(biuroLongClick);
  biuro.attachDoubleClick(biuroDoubleClick);

  poddasze.attachClick(poddaszeClick);

  sypialnia.attachClick(sypialniaClick);

  stasiu.attachClick(stasiuClick);
  stasiu.attachLongPressStop(stasiuLongClick);
  stasiu.attachDoubleClick(stasiuDoubleClick);
}
