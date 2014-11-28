#!/usr/bin/env python
import subprocess
import sys
import math

color_map = [
  { 'threshold': 0,   'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
  { 'threshold': 20,  'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
  { 'threshold': 50,  'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0x00 } },
  { 'threshold': 51,  'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0xFF } },
  { 'threshold': 100, 'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0xFF } },
]

def get_battery_level():
  battery_information = subprocess.Popen('acpi -b | grep -o "[0-9]*%"', shell = True, stdout = subprocess.PIPE).stdout.readlines()
  if battery_information:
    return int(battery_information[0].rstrip()[:-1])
  return 0

def html_hex(color):
  hex_value = str(hex(int(color)))[2:]
  if len(hex_value) == 1:
    return '0' + hex_value
  return hex_value

def write(message):
  sys.stdout.write(message)
  sys.stdout.flush()

if __name__ == '__main__':
  battery_level = get_battery_level()

  for i in range(1, len(color_map)):
    if battery_level < color_map[i]['threshold']:
      break
  lower, upper = color_map[i-1], color_map[i]
  diff = float(upper['threshold'] - lower['threshold'])
  diff_percentage = (battery_level - lower['threshold']) / diff
  lower_percentage = 1 - diff_percentage
  upper_percentage = diff_percentage

  color = {
    'r': math.floor( lower['color']['r'] * lower_percentage + upper['color']['r'] * upper_percentage ),
    'g': math.floor( lower['color']['g'] * lower_percentage + upper['color']['g'] * upper_percentage ),
    'b': math.floor( lower['color']['b'] * lower_percentage + upper['color']['b'] * upper_percentage )
  }

  write('#' + html_hex(color['r']) + html_hex(color['g']) + html_hex(color['b']))
