#!/usr/bin/env python
import sys
import json

if __name__ == '__main__':
  print(json.dumps(sys.stdin.readlines()[0].rstrip())[1:-1])
