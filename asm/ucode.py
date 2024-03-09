#!/usr/bin/env python3
# type: ignore # noqa: PGH003

from __future__ import annotations

from sys import stdin
from pathlib import Path
from functools import reduce

CTRL_WORD = "control-word"
ADDR_WORD = "address-word"
ADDR_INSTR = "address-instruction"
ADDR_OP = "address-operation"
FETCH = "fetch"
INSTR = "instruction"
INSTR_TABLE = "instruction-table"

ENV = (CTRL_WORD, ADDR_WORD, ADDR_INSTR, ADDR_OP, FETCH, INSTR, INSTR_TABLE)

def readline() -> list | None: return list(filter(None, l.strip("\t\r\n").split(" "))) if (l := stdin.readline()) else None
def bitmask(word: list[str], v: list[str]) -> tuple: return reduce(lambda r, x: (r << 1) | int(x in v), [0, *word])
def addrmap(addr: int, word: list[str], v: list[str]) -> int: return reduce(lambda op, x: (op << 1) | (addr >> (len(word) - x - 1)) & 1, [0, *v])

if __name__ == "__main__":
  data = { CTRL_WORD: None, ADDR_WORD: None, ADDR_INSTR: None, ADDR_OP: None, FETCH: [], INSTR: {}, INSTR_TABLE: {} }
  env, iname = None, None
  while (args := readline()) is not None:
    if len(args) == 0: continue
    if args[0][0] == "@":
      env, args = args[0][1:], args[1:]
      assert env in ENV, f"{env} is not a valid environment"
      if env in (CTRL_WORD, ADDR_WORD, ADDR_INSTR, ADDR_OP):
        data[env] = tuple(args)
      elif env == INSTR:
        iname = args[0]
        assert iname not in data[INSTR_TABLE], f"instruction {iname} already defined"
        data[env][iname], data[INSTR_TABLE][int(args[1], base=2)] = [], (iname, bitmask(data[ADDR_WORD], args[2:]))
    else:
      if env == FETCH: data[env].append(bitmask(data[CTRL_WORD], args))
      elif env == INSTR: data[env][iname].append(bitmask(data[CTRL_WORD], args))

  addrw = data[ADDR_WORD]
  addri, addro = tuple(addrw.index(x) for x in data[ADDR_INSTR]), tuple(addrw.index(x) for x in data[ADDR_OP])
  with Path("ucode.bin").open("wb") as f:
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
      print(f"{addr:0{len(data[ADDR_WORD])}b}: {iname:6s} [{opn:02d}] {cw:0{len(data[CTRL_WORD])}b}")
