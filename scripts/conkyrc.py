#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import subprocess
import json

SCRIPT_DIR = '$HOME/scripts/'

colors = {}
colors['white'] = '#FFFFFF'
colors['light-gray'] = '#232D34'
colors['lime'] = '#9FBC00'
colors['urgent'] = '#B33A3A'

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

    self.status_block.set_color(colors['white'])
    self.icon_block.set_color(colors['lime'])

    self.status_block.set_separator(False, 0)
    self.icon_block.set_separator(False, 0)

    self.set_background(colors['light-gray'])

  def set_icon(self, icon):
    self.icon_block.set_full_text('  ' + icon + ' ')

  def set_text(self, text):
    self.status_block.set_full_text(text)

  def set_background(self, background):
    self.icon_block.set_background(background)
    self.status_block.set_background(background)

  def set_border(self, border, border_right, border_top, border_left, border_bottom):
    self.icon_block.set_border(border, border_right, border_top, border_left, border_bottom)
    self.status_block.set_border(border, border_right, border_top, border_left, border_bottom)

  def to_json(self):
    return self.icon_block.to_json() + ',' + self.status_block.to_json()

#########################################
### UTIL ################################
#########################################

def run(command):
  return subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)

def run_script(command):
  return run(SCRIPT_DIR + command)

#########################################
### MODULES #############################
#########################################

def blockify_active_window():
  """ Print the currently active window (or 'none'). """

  call = run('xdotool getactivewindow getwindowname')
  active_window = call.communicate()[0].rstrip()
  if call.returncode != 0:
    active_window = 'none'

  block = StatusUnit('active-window')
  block.set_icon('')
  block.set_text(active_window)

  block.set_border(colors['lime'], False, True, False, False)
  return block.to_json()

def blockify_pidgin():
  """ If pidgin is running, print the number of unread messages.

  For this to work, the pidgin option to set a X variable must be enabled.
  """

  call = run_script('pidgin-count')
  unread_messages = call.communicate()[0].rstrip()
  if call.returncode != 0:
    return None

  block = StatusUnit('pidgin')
  block.set_icon('')
  block.set_text(unread_messages)

  if int(unread_messages) == 0:
    block.set_border(colors['lime'], False, True, False, False)
  else:
    block.set_border(colors['white'], False, True, False, False)
  return block.to_json()

def blockify_volume():
  """ Print the current volume. """

  block = StatusUnit('volume')
  block.icon_block.set_name('toggle-volume')

  status = run_script('volume-control.py status').communicate()[0].rstrip()
  if status == "on":
    block.set_icon('')

    volume = run_script('volume-control.py read').communicate()[0].rstrip()
    block.set_text(volume + '%')

    # TODO avoid second call to volume-control.py inside this script
    color = run_script('volume-color.py').communicate()[0].rstrip()
    block.set_border(color, False, True, False, False)
  else:
    block.set_icon('')
    block.set_text('muted')
    block.set_border(color['urgent'], False, True, False, False)
    block.status_block.set_name('toggle-volume')

  return block.to_json()

def blockify_battery():
  """ Print the current battery level. """

  battery = run('acpi -b | grep -o "[0-9]*%"').communicate()[0].rstrip()[:-1]
  # TODO incorporate this script here
  color = run_script('battery-color.py').communicate()[0].rstrip()

  block = StatusUnit('battery')
  block.set_icon('')
  block.set_text(battery + '%')
  block.set_border(color, False, True, False, False)

  block.status_block.set_min_width(40, 'right')

  return block.to_json()

def blockify_wifi():
  """ Prints information about the connected wifi. """

  return None

def blockify_ethernet():
  """ Prints information about the connected ethernet. """

  return None

def blockify_datetime():
  """ Prints the date and time. """

  return None

#########################################
### MAIN ################################
#########################################

if __name__ == '__main__':
  # TODO
  blocks = [
    blockify_active_window(),
    blockify_pidgin(),
    blockify_volume(),
    blockify_battery(),
    blockify_wifi(),
    blockify_ethernet(),
    blockify_datetime()
  ]

  json = ','.join(block for block in blocks if block)

  sys.stdout.write(json)
  sys.stdout.flush()
