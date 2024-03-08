#!/usr/bin/env python3

from __future__ import annotations

from re import split
from sys import stdin

INSTR = {
  "NOP": (0b0000, 0),
  "LDA": (0b0001, int),
  "STA": (0b0010, int),
  "ADD": (0b0011, int),
  "SUB": (0b0100, int),
  "J": (0b0101, int),
  "JZ": (0b0110, int),
  "JC": (0b0111, int),
  "OUT": (0b1000, 0),
  "HLT": (0b1001, 0)
}

def readline() -> list | None: return list(filter(None, l.strip("\t\r\n").split(" "))) if (l := stdin.readline()) else None

if __name__ == "__main__":
  env, envargs = None, None
  data, i = bytearray(2**4), 0
  while (args := readline()) is not None:
    if len(args) == 0: continue
    cmd, *args = args
    if cmd[0] == ".":
      env, envargs = cmd[1:], args
    elif env == "text":
      assert cmd in INSTR, f"unkown instruction {cmd}"
      op, arg = INSTR[cmd]
      if callable(arg): arg = int(arg(*args)) & 0b1111
      assert isinstance(arg, int), f"invalid argument \"{arg}\" for instruction {cmd}"
      data[i], i = op << 4 | arg, i+1
    elif env == "data":
      data[i], i = int(cmd) & 0b11111111, i+1
  for i in range(len(data)): print(f"{i:02d}: {data[i]:08b}")
