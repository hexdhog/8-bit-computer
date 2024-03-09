# 8-bit computer

Software tools for Ben Eater's 8-bit computer build.

### Programmer

Interface the EEPROM programmer module through USB. No need to hardcode, compile and upload EEPROM
data every time. Just execute `programmer.py` from your computer and send read/write commands to the
programmer module.

### Microcode Compiler

Define the address structure of the microcode EEPROMs (operation number, instruction code, flags, or
more...), the control word and assembly instructions' micrcode. Compile to a binary file and write to EEPROM through programmer.

### ASM Compiler

Write assembly programs, compile and upload (manually) to the computer.
