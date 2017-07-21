#!/usr/bin/env python3


from sys import argv, stderr, stdout

from bakery import render_path


if len(argv) != 2:
    stderr.write("Usage:  render.py NAME\n")
    exit(1)
stdout.write(render_path(argv[1]))
