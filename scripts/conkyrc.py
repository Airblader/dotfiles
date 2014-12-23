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

SCRIPT_DIR = '$HOME/scripts/'

colors = {}
colors['white'] = '#FFFFFF'
colors['light-gray'] = '#232D34'
colors['lime'] = '#9FBC00'
colors['urgent'] = '#B33A3A'
colors['yellow'] = '#E5E511'

class StatusBlock:
  def __init__(self, name):
    self.block = {}
    self.set_name(name)

  def set_key(self, key, value):
    self.block[key] = value

  def set_name(self, name):
    self.block['name'] = name

  def set_full_text(self, full_text):
    self.set_key('full_text', full_text)

  def set_color(self, color):
    self.set_key('color', color)

  def set_background(self, background):
    self.set_key('background', background)

  def set_separator(self, separator, block_width):
    if not separator:
      self.set_key('separator', separator)
    self.set_key('separator_block_width', block_width)

  def set_border(self, border, border_right, border_top, border_left, border_bottom):
    self.set_key('border', border)
    if not border_right:
      self.set_key('border_right', border_right)
    if not border_top:
      self.set_key('border_top', border_top)
    if not border_left:
      self.set_key('border_left', border_right)
    if not border_bottom:
      self.set_key('border_bottom', border_right)

  def set_min_width(self, min_width, align):
    self.set_key('min_width', min_width)
    self.set_key('align', align)

  def to_json(self):
    return json.dumps(self.block)

class StatusUnit:
  def __init__(self, name):
    self.icon_block = StatusBlock(name)
    self.status_block = StatusBlock(name)

    self.set_color(colors['lime'], colors['white'])
    self.status_block.set_separator(False, 0)
    self.icon_block.set_separator(False, 0)

  def set_color(self, icon_color, text_color):
    self.icon_block.set_color(icon_color)
    self.status_block.set_color(text_color)

  def set_icon(self, icon):
    self.icon_block.set_full_text('  ' + icon + ' ')

  def set_text(self, text):
    self.status_block.set_full_text(text + '  ')

  def set_background(self, background):
    self.icon_block.set_background(background)
    self.status_block.set_background(background)

  def set_border(self, border, border_right, border_top, border_left, border_bottom):
    self.icon_block.set_border(border, border_right, border_top, border_left, border_bottom)
    self.status_block.set_border(border, border_right, border_top, border_left, border_bottom)

  def set_urgent(self):
    self.status_block.set_key('urgent', True)
    self.icon_block.set_key('urgent', True)

  def to_json(self):
    return self.icon_block.to_json() + ',' + self.status_block.to_json()

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

  block.set_border(colors['lime'], False, True, False, False)
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

  if int(unread_messages) == 0:
    block.set_border(colors['lime'], False, True, False, False)
  else:
    block.set_urgent()
  return block.to_json()

def blockify_volume():
  """ Print the current volume. """

  block = StatusUnit('volume')
  block.icon_block.set_name('toggle-volume')

  status = run_script('volume-control.py status')[0]
  if status == "on":
    block.set_icon('')

    volume = run_script('volume-control.py read')[0]
    block.set_text(volume + '%')

    color = run_script('volume-color.py ' + volume)[0]
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

  acpi = run('acpi')[0]
  battery = re.search('\d*%', acpi).group(0)
  battery_int = int(battery[:-1])
  is_charging = bool(re.search('Charging', acpi))

  blink_color = None
  if battery_int < 99 and not is_charging:
    blink_color = colors['yellow']

  if blink_color and int(time.time()) % 2:
    block.icon_block.set_color(blink_color)

  block.set_text(battery)

  if battery_int > 10 or is_charging:
    color = get_color_gradient(battery_int, [ 
      { 'threshold': 0,   'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
      { 'threshold': 20,  'color': { 'r': 0xB3, 'g': 0x3A, 'b': 0x3A } },
      { 'threshold': 50,  'color': { 'r': 0xFF, 'g': 0xFF, 'b': 0x00 } },
      { 'threshold': 70,  'color': { 'r': 0x9F, 'g': 0xBC, 'b': 0x00 } },
      { 'threshold': 100, 'color': { 'r': 0x9F, 'g': 0xBC, 'b': 0x00 } } ])
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

  # TODO speed?
  info = basiciw.iwinfo(interface)

  block = StatusUnit('network')
  block.set_icon('')
  block.set_text(info['essid'])
  block.set_border(colors['lime'], False, True, False, False)

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
  block.set_border(colors['lime'], False, True, False, False)

  return block.to_json()

def blockify_datetime():
  """ Prints the date and time. """

  now = datetime.datetime.now()

  calendar = StatusUnit('calendar')
  clock = StatusUnit('clock')

  calendar.set_icon('')
  clock.set_icon('')

  calendar.set_text(now.strftime('%a., %d. %b. %Y'))
  clock.set_text(now.strftime('%H:%M:%S'))

  calendar.set_border(colors['lime'], False, True, False, False)
  clock.set_border(colors['lime'], False, True, False, False)

  return calendar.to_json() + ',' + clock.to_json()

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
    blockify_datetime()
  ]

  separator = ',' + blockify_separator() + ','
  json = separator.join(block for block in blocks if block)

  sys.stdout.write(json)
  sys.stdout.flush()
