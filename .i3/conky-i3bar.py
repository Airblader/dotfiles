#!/usr/bin/env python
import os
import sys
import json

def write(message):
  sys.stdout.write(message + '\n')
  sys.stdout.flush()

def read():
  try:
    line = sys.stdin.readline().strip()
    if not line:
      sys.exit(3)
    return line
  except KeyboardInterrupt:
    sys.exit()

if __name__ == '__main__':
  write('{ "version": 1, "stop_signal": 10, "cont_signal": 12, "click_events": true }')
  write('[[]')

  os.system('conky -d -c ~/.conkyrc')

  while True:
    line, prefix = read(), ''
    if line.startswith(','):
      line, prefix = line[1:], ','

    try:
      parsed = json.loads(line)
    except:
      continue

    x, y = parsed['x'], parsed['y']
    module = parsed['name']

    if module == 'calendar':
      os.system('gsimplecal')
    elif module == 'toggle-volume':
      os.system('$HOME/.i3/volume-control.py toggle')
