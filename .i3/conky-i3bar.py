#!/usr/bin/env python
import os
import sys
import subprocess
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

def run(command):
  return subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)

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
    button = int(parsed['button'])

    try:
      if module == 'calendar':
        run('gsimplecal')
      elif module == 'volume':
        if button == 1:
          os.system('$HOME/scripts/volume-control.py up 10')
        elif button == 3:
          os.system('$HOME/scripts/volume-control.py down 10')
      elif module == 'toggle-volume':
        run('$HOME/scripts/volume-control.py toggle')
    except:
      pass
