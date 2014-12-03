#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import json
import netifaces
import basiciw
import datetime

SCRIPT_DIR = '$HOME/scripts/'

colors = {}
colors['white'] = '#FFFFFF'
colors['light-gray'] = '#232D34'
colors['lime'] = '#9FBC00'
colors['urgent'] = '#B33A3A'
colors['separator'] = '#E5E511'

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

    #self.set_background(colors['light-gray'])

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

  battery = run('acpi -b | grep -o "[0-9]*%"')[0][:-1]
  # TODO incorporate this script here and then use set_urgent
  color = run_script('battery-color.py')[0]

  block.set_text(str(battery) + '%')
  block.set_border(color, False, True, False, False)

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
  block.set_text(interface + '  ' + netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr'])
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
  block.set_color(colors['separator'])
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
