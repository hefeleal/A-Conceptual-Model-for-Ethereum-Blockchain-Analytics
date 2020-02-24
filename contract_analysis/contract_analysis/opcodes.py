#!/usr/bin/python3

opcodes = [
# 0x00
"STOP", "ADD", "MUL", "SUB", "DIV", "SDIV", "MOD", "SMOD", "ADDMOD", "MULMOD", "EXP", "SIGNEXTEND",
"-", "-", "-", "-",

# 0x10
"LT", "GT", "SLT", "SGT", "EQ", "ISZERO", "AND", "OR", "XOR", "NOT", "BYTE",
"-", "-", "-", "-", "-",

# 0x20
"SHA3",
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0x30
"ADDRESS", "BALANCE", "ORIGIN", "CALLER", "CALLVALUE", "CALLDATALOAD", "CALLDATASIZE", "CALLDATACOPY", "CODESIZE", "CODECOPY", "GASPRICE", "EXTCODESIZE", "EXTCODECOPY", "RETURNDATASIZE", "RETURNDATACOPY",
"-",

# 0x40
"BLOCKHASH", "COINBASE", "TIMESTAMP", "NUMBER", "DIFFICULTY", "GASLIMIT",
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0x50
"POP", "MLOAD", "MSTORE", "MSTORE8", "SLOAD", "SSTORE", "JUMP", "JUMPI", "PC", "MSIZE", "GAS", "JUMPDEST",
"-", "-", "-", "-",

# 0x60 - 0x70
"PUSH1 0x", "PUSH2 0x", "PUSH3 0x", "PUSH4 0x", "PUSH5 0x", "PUSH6 0x", "PUSH7 0x", "PUSH8 0x", "PUSH9 0x", "PUSH10 0x", "PUSH11 0x", "PUSH12 0x", "PUSH13 0x", "PUSH14 0x", "PUSH15 0x", "PUSH16 0x",
"PUSH17 0x", "PUSH18 0x", "PUSH19 0x", "PUSH20 0x", "PUSH21 0x", "PUSH22 0x", "PUSH23 0x", "PUSH24 0x", "PUSH25 0x", "PUSH26 0x", "PUSH27 0x", "PUSH28 0x", "PUSH29 0x", "PUSH30 0x", "PUSH31 0x", "PUSH32 0x",

# 0x80
"DUP1", "DUP2", "DUP3", "DUP4", "DUP5", "DUP6", "DUP7", "DUP8", "DUP9", "DUP10", "DUP11", "DUP12", "DUP13", "DUP14", "DUP15", "DUP16",

# 0x90
"SWAP1", "SWAP2", "SWAP3", "SWAP4", "SWAP5", "SWAP6", "SWAP7", "SWAP8", "SWAP9", "SWAP10", "SWAP11", "SWAP12", "SWAP13", "SWAP14", "SWAP15", "SWAP16",

# 0xa0
"LOG0", "LOG1", "LOG2", "LOG3", "LOG4",
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0xb0
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0xc0
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0xd0
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0xe0
"-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-",

# 0xf0
"CREATE", "CALL", "CALLCODE", "RETURN", "DELEGATECALL", "-", "-", "-", "-", "-", "STATICCALL", "-", "-", "REVERT", "INVALID", "SELFDESTRUCT"
]
