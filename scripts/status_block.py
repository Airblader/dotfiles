#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from color_definitions import colors

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
    self.set_key('border_right', border_right)
    self.set_key('border_top', border_top)
    self.set_key('border_left', border_left)
    self.set_key('border_bottom', border_bottom)

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
    self.icon_block.set_full_text(icon)

  def set_text(self, text):
    self.status_block.set_full_text(text)

  def set_background(self, background):
    self.icon_block.set_background(background)
    self.status_block.set_background(background)

  def set_border(self, border, border_right, border_top, border_left, border_bottom):
    self.icon_block.set_border(border, 0, border_top, border_left, border_bottom)
    self.status_block.set_border(border, border_right, border_top, 0, border_bottom)

  def set_urgent(self):
    self.status_block.set_key('urgent', True)
    self.icon_block.set_key('urgent', True)

  def to_json(self):
    return self.icon_block.to_json() + ',' + self.status_block.to_json()
