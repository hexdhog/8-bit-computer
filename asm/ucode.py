#!/usr/bin/env python3
# type: ignore # noqa: PGH003

from __future__ import annotations

from os import getenv
from pathlib import Path
from functools import reduce
from helper import tokens, parse_instr
from argparse import ArgumentParser, BooleanOptionalAction

DEBUG = int(getenv("DEBUG", "0"))

CTRL_WORD = "control-word"
ADDR_WORD = "address-word"
ADDR_INSTR = "address-instruction"
ADDR_OP = "address-operation"
FETCH = "fetch"
INSTR = "instruction"
INSTR_TABLE = "instruction-table"

ENV = (CTRL_WORD, ADDR_WORD, ADDR_INSTR, ADDR_OP, FETCH, INSTR, INSTR_TABLE)

def bitmask(word: list[str], v: list[str]) -> tuple: return reduce(lambda r, x: (r << 1) | int(x in v), [0, *word])
def addrmap(addr: int, word: list[str], v: list[str]) -> int: return reduce(lambda op, x: (op << 1) | (addr >> (len(word) - x - 1)) & 1, [0, *v])

if __name__ == "__main__":
  parser = ArgumentParser(description="8-bit computer microcode compiler")
  parser.add_argument("ucode", help="assembly code file path")
  parser.add_argument("-o", "--out", help="output file path")
  parser.add_argument("-v", "--verbose", action=BooleanOptionalAction, help="enable verbose output")
  args = vars(parser.parse_args())
  if DEBUG > 0: print(args, end="\n\n")

  data = { CTRL_WORD: None, ADDR_WORD: None, ADDR_INSTR: None, ADDR_OP: None, FETCH: [], INSTR: {}, INSTR_TABLE: {} }
  env, iname = None, None
  for t in tokens(Path(args["ucode"]).read_text()):
    if t[0][0] == "@":
      env, envargs = t[0][1:], t[1:]
      assert env in ENV, f"{env} is not a valid environment"
      if env in (CTRL_WORD, ADDR_WORD, ADDR_INSTR, ADDR_OP):
        data[env] = tuple(envargs)
      elif env == INSTR:
        iname = envargs[0]
        assert iname not in data[INSTR_TABLE], f"instruction {iname} already defined"
        data[env][iname], data[INSTR_TABLE][parse_instr(envargs[1])[0][0]] = [], (iname, bitmask(data[ADDR_WORD], envargs[2:]))
    elif env == FETCH: data[env].append(bitmask(data[CTRL_WORD], t))
    elif env == INSTR: data[env][iname].append(bitmask(data[CTRL_WORD], t))
  if DEBUG > 0: print(data, end="\n\n")

  addrw = data[ADDR_WORD]
  addri, addro = tuple(addrw.index(x) for x in data[ADDR_INSTR]), tuple(addrw.index(x) for x in data[ADDR_OP])
  with Path(args["out"]).open("wb") as f:
    for addr in range(2**len(data[ADDR_WORD])):
      instr, opn = addrmap(addr, addrw, addri), addrmap(addr, addrw, addro)
      cw, iname = 0, ""
      if instr in data[INSTR_TABLE]:
        iname, ifaddr = data[INSTR_TABLE][instr]
        if opn < len(data[FETCH]):
          cw = data[FETCH][opn]
        else:
          ops, opi = data[INSTR][iname], opn - len(data[FETCH])
          if opi < len(ops) and (ifaddr == 0 or ifaddr & addr != 0): cw = ops[opi]
      f.write(cw.to_bytes(int(len(data[CTRL_WORD]) / 8), byteorder="big", signed=False))
      if args["verbose"]: print(f"{addr:0{len(data[ADDR_WORD])}b}: {iname:6s} [{opn:02d}] {cw:0{len(data[CTRL_WORD])}b}")
