#!/usr/bin/env python3


from sys import argv, stderr, stdout

from template import render_path


if len(argv) != 2:
    print("Usage:  render.py NAME", file=stderr)
    exit(1)
stdout.write(render_path(argv[1]))