#!/usr/bin/env python3
# type: ignore # noqa: PGH003

from __future__ import annotations

import time

from os import getenv
from pathlib import Path
from argparse import ArgumentParser
from binascii import hexlify, unhexlify
from serial import Serial, EIGHTBITS, PARITY_NONE, STOPBITS_ONE

DEBUG = int(getenv("DEBUG", "0"))
HEXDUMP_SIZE = int(getenv("HEXDUMP_SIZE", "16"))

BO = "big"
HEADER, HEADER_SIZE = 0xcafebabe, 4
ACTION_READ, ACTION_WRITE = 0x00, 0x01

def now_ms() -> int: return round(time.time() * 1000)
def bytes2hex(b: bytes) -> str: return hexlify(b).decode("utf-8")
def send(ser: Serial, data: bytes, timeout: int = 0) -> bytes:
  if DEBUG > 1: print(f"[send]: {bytes2hex(data)}")
  ser.write(data)
  data, start, last = b"", now_ms(), None
  # read serial until timeout is reached or debounce timeout is reached
  while (timeout <= 0 or now_ms() - start < timeout) and (last is None or now_ms() - last < 100):
    if ser.in_waiting: data, last = data + ser.read(ser.in_waiting), now_ms()
  if DEBUG > 1: print(f"[recv]: {bytes2hex(data)}")
  return data

def cmd(ser: Serial, addr: int, size: int, data: bytes | None = None, timeout: int = 0) -> bytes:
  cmd = bytearray()
  cmd += HEADER.to_bytes(HEADER_SIZE, byteorder=BO, signed=False)
  cmd += (ACTION_WRITE if isinstance(data, (bytes, bytearray)) else ACTION_READ).to_bytes(1, byteorder=BO, signed=False)
  cmd += (addr << 16 | size).to_bytes(4, byteorder=BO, signed=False)
  if isinstance(data, (bytes, bytearray)): cmd += data
  data = send(ser, cmd, timeout)
  return data[9:9+int.from_bytes(data[7:9])] if len(data) >= HEADER_SIZE + 5 and int.from_bytes(data[:4]) == HEADER else b""

def read(ser: Serial, addr: int, size: int, timeout: int = 0) -> bytes: return cmd(ser, addr, size, timeout=timeout)
def write(ser: Serial, addr: int, size: int, data: bytes, timeout: int = 0) -> bytes: return cmd(ser, addr, size, data, timeout)

if __name__ == "__main__":
  parser = ArgumentParser(description="8-bit computer EEPROM programmer")
  parser.add_argument("port", help="UART port the programmer is connected to")
  parser.add_argument("-a", "--addr", help="address to read/write [default=0]", default="0")
  parser.add_argument("-s", "--size", help="size to read", default="0")
  parser.add_argument("-c", "--count", help="number of write data chunks [default=1]", default="1")
  parser.add_argument("-d", "--data", help="data to write in hexadecimal")
  parser.add_argument("-f", "--file", help="binary file to write to EEPROM")
  parser.add_argument("-t", "--timeout", help="read/write operation timeout in milliseconds (0 for no timeout) [default=1000]", default="1000")
  parser.add_argument("--block-size", help="read/write in blocks of x bytes [default=64]", default="64")
  parser.add_argument("--data-step",
    help="""write data step (will write every x'th byte from --data-offset;
      e.g. 3 will write 1 byte, skip the next two, and write the following) [default=1]""",
    default="1")
  parser.add_argument("--data-offset", help="write data offset (will write data from x'th byte) [default=0]", default="0")
  args = vars(parser.parse_args())
  if DEBUG > 0: print(args)

  ser = Serial(args["port"], baudrate=115200, bytesize=EIGHTBITS, parity=PARITY_NONE, stopbits=STOPBITS_ONE)
  addr, size, count, bs, ds, do, to = (int(args[x], 0) for x in ("addr", "size", "count", "block_size", "data_step", "data_offset", "timeout"))
  data, file = args["data"], args["file"]
  assert not all(x is not None for x in (data, file)), "both data and file specified, only one can be used at a time"
  if file is not None: data = Path(file).read_bytes()
  elif isinstance(data, str): data = unhexlify(data)
  if data is not None: data = data[do::ds] * count

  try:
    # wait for microcontroller to respond before sending any command
    while len(read(ser, 0x00, 1, 100)) == 0: time.sleep(0.1)
    if data is not None:
      for a, d in ((addr+i, data[i:i+bs]) for i in range(0, len(data), bs)): write(ser, a, len(d), d, to)
    if size > 0:
      data = b"".join(read(ser, addr+i, bs if bs+i <= size else size-i, to) for i in range(0, size, bs))
      for i, d in ((addr+i, data[i:i+HEXDUMP_SIZE]) for i in range(0, len(data), HEXDUMP_SIZE)):
        b, s = " ".join(f"{x:02x}" for x in d), "".join(chr(x) if 33 <= x <= 126 else "." for x in d)
        print(f"{i:08x}: {b:47s} |{s:<16s}|")
  finally:
    ser.close()
