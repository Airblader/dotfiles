#!/usr/bin/env python
import sys
import json

if __name__ == '__main__':
  try:
    sys.stdout.write(json.dumps(sys.stdin.readlines()[0].rstrip())[1:-1])
    sys.stdout.flush()
  except:
    pass
