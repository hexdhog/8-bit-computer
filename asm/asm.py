#!/usr/bin/env python3

from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import Generator
from argparse import ArgumentParser

DEBUG = int(getenv("DEBUG", "0"))

def tokens(s: str) -> Generator: return (x for x in (list(filter(None, l.strip("\t\r\n").split(" "))) for l in s.split("\n")) if len(x) > 0)
def parse_instr(instr: str) -> tuple:
    op, args = instr.split("(")
    args = args.strip(")")
    if all(x.isdigit() for x in args):
      pos = [x for _, x in sorted([(int(x), [len(args)-i-1 for i, v in enumerate(args) if x == v]) for x in set(args)])]
    else:
      pos = []
    return (int(op, 2), len(op)), (pos, len(args))

if __name__ == "__main__":
  parser = ArgumentParser(description="8-bit computer assembly compiler")
  parser.add_argument("asm", help="assembly code file path")
  parser.add_argument("-u", "--ucode", help="microcode file path")
  args = vars(parser.parse_args())
  if DEBUG > 0: print(args, end="\n\n")

  instr = { t[1]: parse_instr(t[2]) for t in tokens(Path(args["ucode"]).read_text()) if t[0] == "@instruction" }
  if DEBUG > 0: print("\n".join([f"{k}:\t{v}" for k, v in instr.items()]), end="\n\n")

  env, op = None, None
  data = bytearray()
  for t in tokens(Path(args["asm"]).read_text()):
    cmd, *cmdargs = t
    if cmd[0] == ".":
      env, envargs = cmd[1:], cmdargs
    elif env == "text":
      assert cmd in instr, f"unkown instruction {cmd}"
      opcode, opargs = instr[cmd]
      op = (opcode[0] & ((1 << opcode[1]) - 1)) << opargs[1]

      oparg = 0
      for i, pos in enumerate(opargs[0]):
        v = int(cmdargs[i], 0) & ((1 << len(pos)) - 1)
        for j, x in enumerate(pos):
          oparg |= ((v >> (len(pos) - j - 1)) & 1) << x
      oparg &= (1 << opargs[1]) - 1

      data += (op | oparg).to_bytes(round((opcode[1] + opargs[1]) / 8), byteorder="big")
    elif env == "data":
      data += int(cmd, 0).to_bytes(1, byteorder="big")

  for i in range(len(data)): print(f"{i:04d}: {data[i]:08b}")
