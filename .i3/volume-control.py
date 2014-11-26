#!/usr/bin/env python
import subprocess
import sys

def get_active_sink():
  process = subprocess.Popen('pacmd list-sinks | grep "* index" | awk \'{print $3}\'', shell = True, stdout = subprocess.PIPE)
  return process.stdout.readlines()[0].rstrip()

def get_volume():
  process = subprocess.Popen('amixer -D pulse get Master | grep -o "\[.*%\]" | grep -o "[0-9]*" | head -n1', shell = True, stdout = subprocess.PIPE)
  return process.stdout.readlines()[0]

def set_volume(percentage):
  subprocess.Popen('pactl set-sink-volume ' + get_active_sink() + ' ' + str(percentage) + '%', shell = True, stdout = subprocess.PIPE)

def toggle_volume():
  subprocess.Popen('amixer -D pulse set Master Playback Switch toggle', shell = True, stdout = subprocess.PIPE)

def is_muted():
  process = subprocess.Popen('amixer -D pulse get Master | grep -o "\[on\]" | head -n1', shell = True, stdout = subprocess.PIPE)
  return not process.stdout.readlines()

def write(message):
  sys.stdout.write(message)
  sys.stdout.flush()

def trim_to_range(volume):
  volume = int(volume)
  if volume < 0:
    volume = 0
  elif volume > 200:
    volume = 200
  return volume

if __name__ == '__main__':
  command = sys.argv[1]

  if command == 'set':
    set_volume(trim_to_range(sys.argv[2]))
  elif command == 'up':
    new_volume = trim_to_range(int(get_volume()) + int(sys.argv[2]))
    set_volume(new_volume)
  elif command == 'down':
    new_volume = trim_to_range(int(get_volume()) - int(sys.argv[2]))
    set_volume(new_volume)
  elif command == 'toggle':
    toggle_volume()
  elif command == 'read':
    write(get_volume())
  elif command == 'status':
    if int(get_volume()) == 0:
      write('muted')
    elif is_muted():
      write('muted')
    else:
      write('on')
  else:
    write('Usage: ' + sys.argv[0] + ' [set|up|down|toggle|read|status] [value]\n')
