#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import netifaces
import basiciw
import time
import datetime
import re

from jsonpath_rw import jsonpath, parse

import volume_control
import executor
from color_definitions import colors
from gradient import get_color_gradient
from status_block import StatusBlock, StatusUnit

def blockify_active_window():
  """ Print the currently active window (or 'none'). """

  active_window, return_code = executor.run('xdotool getactivewindow getwindowname')
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

  unread_messages, return_code = executor.run_script('pidgin-count')
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

    color = get_color_gradient(int(volume), [ 
      { 'threshold': 0,   'color': colors['urgent'] },
      { 'threshold': 100, 'color': colors['blue'] },
      { 'threshold': 101, 'color': colors['yellow'] },
      { 'threshold': 200, 'color': colors['yellow'] } ])
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

  acpi = executor.run('acpi -b')[0]
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
      { 'threshold': 0,   'color': colors['urgent'] },
      { 'threshold': 20,  'color': colors['urgent'] },
      { 'threshold': 80,  'color': colors['blue'] },
      { 'threshold': 100, 'color': colors['blue'] } ])
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
