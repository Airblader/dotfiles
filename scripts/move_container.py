#!/usr/bin/env python
import sys
import subprocess
import json

def run(command):
  return subprocess.Popen(command, shell = True, stdout = subprocess.PIPE).stdout.readlines()

if __name__ == '__main__':
  workspaces = json.loads(''.join(run('i3-msg -t get_workspaces')))
  tree = json.loads(''.join(run('i3-msg -t get_tree')))

  target = sys.argv[1]

  focused_workspace_num = None
  for workspace in workspaces:
    if workspace['focused']:
      focused_workspace_num = workspace['num']
      break

  focused_workspace = None
  for node in tree['nodes'][1]['nodes'][1]['nodes']:
    if node['num'] == focused_workspace_num:
      focused_workspace = node
      break

  run('i3-msg move container to workspace ' + target)
  if len(focused_workspace['nodes']) == 1:
    run('i3-msg workspace ' + target)
