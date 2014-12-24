#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import math
import json
import netifaces
import basiciw
import time
import datetime
import re

from jsonpath_rw import jsonpath, parse

import volume_control
from color_definitions import colors
from status_block import StatusBlock, StatusUnit

SCRIPT_DIR = '$HOME/scripts/'

#########################################
### UTIL ################################
#########################################

def run(command):
  call = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)
  stdout = call.communicate()[0]
  return stdout.strip().decode('utf-8'), call.returncode

def run_script(command):
  return run(SCRIPT_DIR + command)

def i3_msg(type):
  ''' Executes i3-msg -t <type> and returns the parsed JSON output.  '''
  return json.loads(run('i3-msg -t ' + type)[0])

def get_workspace():
  ''' Returns the node of the currently focused workspace. '''
  workspaces = i3_msg('get_workspaces')
  tree = i3_msg('get_tree')

  focused_num = None
  for workspace in workspaces:
    if workspace['focused']:
      focused_num = workspace['num']
      break

  for node in tree['nodes'][1]['nodes'][1]['nodes']:
    if node['num'] == focused_num:
      return node

  return None

# TODO remove a flag which one is the active window
def get_window_titles():
  ''' Returns an array of window titles of the current workspace.  '''

  expression = parse("$..window_properties.title")
  return [match.value for match in expression.find(get_workspace())]

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

#########################################
### MODULES #############################
#########################################

def blockify_active_window():
  """ Print the currently active window (or 'none'). """

  active_window, return_code = run('xdotool getactivewindow getwindowname')
  if return_code != 0:
    return None
  if len(active_window) > 100:
    active_window = active_window[:80] + '...' + active_window[-20:]

  block = StatusUnit('active-window')
  block.set_icon('')
  block.set_text(active_window)

  return block.to_json()

def blockify_pidgin():
  """ If pidgin is running, print the number of unread messages.

  For this to work, the pidgin option to set a X variable must be enabled.
  """

  unread_messages, return_code = run_script('pidgin-count')
  if return_code != 0:
    return None

  block = StatusUnit('pidgin')
  block.set_icon('')
  block.set_text(unread_messages)

  if int(unread_messages) != 0:
    block.set_urgent()
  return block.to_json()

def blockify_volume():
  """ Print the current volume. """

  block = StatusUnit('volume')
  block.icon_block.set_name('toggle-volume')

  status = volume_control.status()
  if status == "on":
    block.set_icon('')

    volume = volume_control.get_volume()
    block.set_text(volume + '%')

    # TODO decode color from hex
    color = get_color_gradient(int(volume), [ 
      { 'threshold': 0,   'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
      { 'threshold': 100, 'color': { 'r': 0x13, 'g': 0x1D, 'b': 0x24 } },
      { 'threshold': 101, 'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0x00 } },
      { 'threshold': 200, 'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0x00 } } ])
    block.set_border(color, False, True, False, False)
    block.status_block.set_min_width(40, 'right')
  else:
    block.set_icon('')
    block.set_text('muted')
    block.set_urgent()
    block.status_block.set_name('toggle-volume')

  return block.to_json()

def blockify_battery():
  """ Print the current battery level. """

  block = StatusUnit('battery')
  block.set_icon('')

  acpi = run('acpi -b')[0]
  battery = re.search('\d*%', acpi).group(0)
  battery_int = int(battery[:-1])
  is_charging = bool(re.search('Charging|Unknown', acpi))

  blink_color = None
  if battery_int < 99 and not is_charging:
    blink_color = colors['urgent']

  if blink_color and int(time.time()) % 2:
    block.icon_block.set_color(blink_color)

  block.set_text(battery)

  if battery_int > 10 or is_charging:
    color = get_color_gradient(battery_int, [ 
      { 'threshold': 0,   'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
      { 'threshold': 20,  'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
      { 'threshold': 80,  'color': { 'r': 0x13, 'g': 0x1D, 'b': 0x24 } },
      { 'threshold': 100, 'color': { 'r': 0x13, 'g': 0x1D, 'b': 0x24 } } ])
    block.set_border(color, False, True, False, False)
  else:
    block.set_urgent()

  block.status_block.set_min_width(40, 'right')
  return block.to_json()

def blockify_wifi():
  """ Prints information about the connected wifi. """

  interface = "wlan0"
  try:
    with open('/sys/class/net/{}/operstate'.format(interface)) as operstate:
      status = operstate.read().strip()
  except:
    return None  
  if status != 'up':
    return None

  info = basiciw.iwinfo(interface)

  block = StatusUnit('network')
  block.set_icon('')
  block.set_text(info['essid'])

  return block.to_json()

# TODO combine with wifi code
# TODO if ethernet is there but not connected, the i3bar disappears :(
def blockify_ethernet():
  """ Prints information about the connected ethernet. """

  interface = "eth0"
  try:
    with open('/sys/class/net/{}/operstate'.format(interface)) as operstate:
      status = operstate.read().strip()
  except:
    return None  
  if status != 'up':
    return None

  block = StatusUnit('network')
  block.set_icon('')
  block.set_text(interface + ' @ ' + netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])

  return block.to_json()

def blockify_date():
  """ Prints the date and time. """

  now = datetime.datetime.now()

  calendar = StatusUnit('calendar')
  calendar.set_icon('')
  calendar.set_text(now.strftime('%a., %d. %b. %Y'))
  return calendar.to_json()

def blockify_time():
  """ Prints the time. """

  now = datetime.datetime.now()

  clock = StatusUnit('clock')
  clock.set_icon('')
  clock.set_text(now.strftime('%H:%M:%S'))
  return clock.to_json()

def blockify_separator():
  block = StatusBlock('separator')
  block.set_full_text('    ')
  block.set_color(colors['yellow'])
  block.set_separator(False, 0)
  return block.to_json()

#########################################
### MAIN ################################
#########################################

if __name__ == '__main__':
  blocks = [
    blockify_active_window(),
    blockify_pidgin(),
    blockify_volume(),
    blockify_battery(),
    blockify_wifi(),
    blockify_ethernet(),
    blockify_date(),
    blockify_time()
  ]

  separator = ',' + blockify_separator() + ','
  json = separator.join(block for block in blocks if block)

  sys.stdout.write(json)
  sys.stdout.flush()
