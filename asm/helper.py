from __future__ import annotations

from typing import Generator

def tokens(s: str) -> Generator:
  lines = (l[:i if (i := l.find("#")) >= 0 else None] for l in s.split("\n"))
  return (x for x in (list(filter(None, l.replace(",", " ").strip("\t\r\n").split(" "))) for l in lines) if len(x) > 0)
def parse_instr(instr: str) -> tuple:
  op, args = instr.split("(")
  args = args.strip(")")
  pos = []
  if all(x.isdigit() for x in args):
    pos = [x for _, x in sorted([(int(x), [len(args)-i-1 for i, v in enumerate(args) if x == v]) for x in set(args)])]
  return (int(op, 2), len(op)), (pos, len(args))
