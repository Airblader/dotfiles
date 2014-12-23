#!/usr/bin/env python3
import subprocess
import sys

def run(command):
  call = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE)
  stdout = call.communicate()[0]
  return stdout.strip().decode('utf-8'), call.returncode

def get_active_sink():
  return run('pacmd list-sinks | grep "* index" | awk \'{print $3}\'')[0]

def get_volume():
  return run('amixer -D pulse get Master | grep -o "\[.*%\]" | grep -o "[0-9]*" | head -n1')[0]

def set_volume(percentage):
  run('pactl set-sink-volume ' + get_active_sink() + ' ' + str(percentage) + '%')

def toggle_volume():
  run('amixer -D pulse set Master Playback Switch toggle')

def is_muted():
  return not run('amixer -D pulse get Master | grep -o "\[on\]" | head -n1')[0]

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

def status():
  if int(get_volume()) == 0 or is_muted():
    return 'muted'
  else:
    return 'on'

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
    write(status())
  else:
    write('Usage: ' + sys.argv[0] + ' [set|up|down|toggle|read|status] [value]\n')
