# 8-bit computer

Software tools for Ben Eater's 8-bit computer build.

## Programmer

Interface the EEPROM programmer module through USB. No need to hardcode, compile and upload EEPROM data every time. Just execute `programmer.py` from your computer and send read/write commands to the programmer module.

## Microcode Compiler

Define the address structure of the microcode EEPROMs (operation number, instruction code, flags, or more...), the control word and assembly instructions' micrcode. Compile to a binary file and write to EEPROM through programmer.

### Syntax

The microcode file is defined using a set of commands:

#### control-word
Define the order and size of the control word.

The following command will declare a 16-bit long control word with the first label corresponding to the MSb of the control word and the last to the LSb.

```
@control-word HLT MI RI RO IO II AI AO SO SU BI OI CE CO JMP FI
```

#### address-word
Define the order and size of the microcode EEPROM address'

The following command will declare an 11-bit address word with the first label corresponding to the MSb of the address word and the last to the LSb.
```
@address-word 0 Z C 0 I3 I2 I1 I0 T2 T1 T0
```

#### address-instruction
Define which bits in `address-word` encode the current assmebly instruction opcode.

The following command will declare that the 4th LSb in `address-word` will become the 1st LSb of the instruction opcode, the 5th LSb in `address-word` will become the 2nd LSb of the instruction opcode, etc.

Therefore, if the current EEPROM address was `0b01110110011`, the current instruction opcode would be `0b0110`.

```
@address-instruction I3 I2 I1 I0
```

#### address-operation
Define which bits in `address-word` encode the current micro operation to execute (all assembly instructions get a fixed amount of clock cycles).

The following command will declare that the 1st LSb in `address-word` will become the 1st LSb of the microcode operation, the 2nd LSb in `address-word` will become the 2nd LSb of the instruction opcode, etc.

Therefore, if the current EEPROM address was `0b01110110011`, the current instruction opcode would be `0b011`.

```
@address-operation T2 T1 T0
```

#### fetch
Define the micro operations to perform a fetch cycle.

The following command will declare a fetch cycle with two micro operations (1uop/line). The first, `MI CO`, indicates that the bits corresponding to the labels `MI` and `CO` in the `control-word` will be set to 1, while the others will be set to 0 (resulting in the control word: `0100000000000100`).

```
@fetch
    MI CO
    RO II CE
```

#### instruction
Declare an assembly instruction, defining its opcode, arguments and conditions to execute (flags).

```
@instruction <name> <opcode>(<arg-mask>) <exec-conditions>
    <uop0>
    <uop1>
    ...
    <uopn>
```

- name: unique name to be used in assembly code to refer to the instruciton
- opcode: unique number identifying the instruction (in binary)
- arg-mask: order of the bits of each instruction argument
- exec-conditions: list of `address-word` labels which determine when the instruction should be executed

The following command will declare the `LDA` assembly instruction with a 4-bit opcode `0001`, one 4-bit argument `0000`, no execution conditions and two micro operations (1uop/line).

```
@instruction LDA 0001(0000)
    IO MI
    RO AI
```

The following command will declare the `ADDIS` assembly instruction with a 4-bit opcode `1010`, and reserve space for two 2-bit arguments `0011 -> arg0_bit1 | arg0_bit0 | arg1_bit1 | arg2_bit0`.

```
@instruction ADDIS 1010(0011)
    ...
```

For example, the assembly instruction `ADDIS 3 2` will take the first argument (3) encode its two least significant bits to the two most significant bits of the instruction argument section (`3 = 0b11 -> 11xx`) and take the second argument (2) encode its two least significant bits to the two least significant bits of the instruction argument section (`2 = 0b10 -> xx10`). Therefore, the complete encoded instruction will be `10101110`.

Finally, the following instruction will declare the `JZC` assembly instruction which will only execute when bits `C` and `Z` from the `address-word` are set to 1.

```
@instruction JCZ 0110(0000) C Z
    IO JMP
```

## ASM Compiler

Write assembly programs, compile and upload (manually) to the computer.

### Syntax

The code is split into two sections: `.text` for assembly code, and `.data` for static data.

```
.text
    <asm instr. 1>
    <asm instr. 2>
    ...
    <asm instr. n>

.data
    <data 0>
    <data 1>
    ...
    <data 2>
```

For example, the following code calculates the fibonacci sequence:

```asm
.text
    LDA 9   # load value at address 9 (first value in data section) to A register
    ADD 10  # load value at address 10 (second value in data section) and add the value to register A
    OUT     # display value of register A on the 7-segment display
    STA 10  # store the value of register A to address 10
    ADD 9   # load value at address 9 and add the value to register A
    OUT     # display value of register A on the 7-segment display
    STA 9   # store the value of register A to address 9
    J 1     # jump to the instruction at address 1 (ADD 10)
    HLT     # halt the computer

.data
    0       # store a 0 at address 9
    1       # store a 1 at address 10
```
