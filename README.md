UE2asm is an assembler for Usagi Electrics proposed UE2 vacuum tube computer:

As proposed the UE2 will have 4096 12-bit words of memory arranged into 16
banks of 256 words, 2 12-bit registers: a 12 bit accumulator (AC), and a
memory access register (HC). Opcodes for the UE2 contain the operation in
the top 4 bits of the word, and operands (if any) in thhe lower 8 bits

see UE2 documentation for opcode definitions.

The format of input files for ue2asm is that each line of the file will
be in the following format:
```
[<label>:] [<mnemonic> [<argument>]] [;<comment>]
```

a label can be any string using the chraracters _,0-9,a-z,A-Z, but must
start with an underscore _ or a letter.

The mnemonic can be any of the 16 mnemonics for the opcodes of UE2 or
either of two pseudo-ops provideded by ue2asm. The DW mnemonic stores
a raw word at that point in the code, and ORG which sets the base
address for subsequent opcodes.

The argument can be any expression using basic arithmatic operations.
operands can be decimal numbers, hex numbers (prefixed with 0x), 
octal numbers (prefixed with 0o), labels, or $ (which is used to 
indicate the current word address)

Comments start with ; and all text after the semicolon is ignored by 
the assembler
