#!/usr/bin/env python3
import math

def html_hex(color):
  hex_value = str(hex(int(color)))[2:]
  if len(hex_value) == 1:
    return '0' + hex_value
  return hex_value

def get_color_gradient(percentage, color_map):
  for i in range(1, len(color_map)):
    if percentage < color_map[i]['threshold']:
      break
  lower, upper = color_map[i-1], color_map[i]
  diff = float(upper['threshold'] - lower['threshold'])
  diff_percentage = (percentage - lower['threshold']) / diff
  lower_percentage = 1 - diff_percentage
  upper_percentage = diff_percentage

  color = {
    'r': math.floor( lower['color']['r'] * lower_percentage + upper['color']['r'] * upper_percentage ),
    'g': math.floor( lower['color']['g'] * lower_percentage + upper['color']['g'] * upper_percentage ),
    'b': math.floor( lower['color']['b'] * lower_percentage + upper['color']['b'] * upper_percentage )
  }

  return '#' + html_hex(color['r']) + html_hex(color['g']) + html_hex(color['b'])
