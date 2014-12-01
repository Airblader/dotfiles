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

class StatusBlock:
  def __init__(self, name):
    self.block = {}
    self.block['name'] = name

  def set_key(self, key, value):
    self.block[key] = value

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
  call = run('xdotool getactivewindow getwindowname')
  active_window = call.communicate()[0].rstrip()
  if call.returncode != 0:
    active_window = 'none'

  block = StatusUnit('active-window')
  block.set_icon('')
  block.set_text(active_window)

  block.set_border(colors['lime'], False, True, False, False)

  return block.to_json()

#########################################
### MAIN ################################
#########################################

if __name__ == '__main__':
  print str(blockify_active_window())
