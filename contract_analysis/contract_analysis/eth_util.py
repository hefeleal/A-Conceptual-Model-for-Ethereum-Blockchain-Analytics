#!/usr/bin/python3
# coding=utf-8

import functools

import ethereum.utils as eth

import opcodes

eth_in_wei = 1000000000000000000

# returns a tuple containing the contract creation code, the actual SC code,
# and the constructor arguments
# - contract creation code is up until the first STOP after the first CODECOPY
# - constructor arguments start after the last STOP after which there is
#   an unknown operation (or simply after the last STOP of the code if there
#   is no unknown operation thereafter)
# 
# will always return three bytecodes that each start with "0x"
def extract_contract_code(original_bytecode):
    bytecode = prepend_0x(original_bytecode)
    if bytecode[:4] != "0x60": # PUSH1
        return ("0x", bytecode, "0x")
    i = 2
    found_code_copy = False
    actual_code_start = len(bytecode)
    last_stop_position = len(bytecode)
    while i < len(bytecode):
        current = int(bytecode[i:i+2], 16)
        opcode_length = 2
        if current == 0x39: # CODECOPY
            found_code_copy = True
        elif current == 0x60 and bytecode[i+2:i+4] != "" and int(bytecode[i+2:i+4], 16) >= 0x60 \
            and found_code_copy and actual_code_start == len(bytecode):  # PUSH1 0x60 or so
            actual_code_start = i
            opcode_length = 4
        elif current >= 0x60 and current <= 0x7f:
            opcode_length = 2 + 2 * (current - 0x5f)
        elif current == 0x00: # STOP
            last_stop_position = i + 2
        elif is_unknown_opcode(current):
            break
        i += opcode_length
    if not found_code_copy:
        return ("0x", bytecode, "0x")
    if actual_code_start == len(bytecode) or last_stop_position == len(bytecode):
        return ("0x", bytecode, "0x")
    return (prepend_0x(bytecode[:actual_code_start]), prepend_0x(bytecode[actual_code_start:last_stop_position]), prepend_0x(bytecode[last_stop_position:]))

# prepends a "0x" to a string if it doesn't already start with it.
def prepend_0x(string):
    if string[:2] == "0x":
        return string
    else:
        return "0x" + string

def is_unknown_opcode(code):
    return opcodes.opcodes[code] == "-"

# function gives the same result, no matter if `bytecode` starts with "0x" or not
def bytecode_to_opcodes_with_offsets(bytecode):
    res = []
    if bytecode[:2] == "0x":
        bytecode_to_decode = bytecode[2:]
    else:
        bytecode_to_decode = bytecode
    i = 0
    while i < len(bytecode_to_decode):
        current = int(bytecode_to_decode[i:i+2], 16)
        opcode_length = 2
        if current >= 0x60 and current <= 0x7f:
            opcode_length = 2 + 2 * (current - 0x5f)
        res.append(("{0:#06x}".format(int(i/2)), opcodes.opcodes[current] + bytecode_to_decode[i+2:i+opcode_length]))
        i += opcode_length
    return res

# function gives the same result, no matter if `bytecode` starts with "0x" or not
def bytecode_to_opcodes(bytecode):
    return list(map(lambda x: x[1], bytecode_to_opcodes_with_offsets(bytecode)))

# function gives the same result, no matter if `bytecode` starts with "0x" or not
def bytecode_to_opcodes_pretty(bytecode):
    opcodes = bytecode_to_opcodes_with_offsets(bytecode)
    for o in opcodes:
        print(o[0] + "\t" + o[1])

# this function also works for opcode lists with relative PUSH2 instructions that
# come from the sanitize_opcodes function. The relative jump locations are then 
# replaced by "x"s
# However the opc parameter must be a list, not a list of tuples
def opcodes_to_bytecode(opc):
    res = ""
    for o in opc:
        splitted = o.split(" ")
        if len(splitted) > 1:
            opcode_number = opcodes.opcodes.index(splitted[0] + " 0x")
            second_part = ""
            if splitted[1][0] == "+" or splitted[1][0] == "-":
                second_part = "x" * (opcode_number - 0x5f)*2
            else:
                second_part = splitted[1][2:]
            res += hex(opcode_number)[2:] + second_part
        else:
            res += "{0:02x}".format(opcodes.opcodes.index(splitted[0]))
    return res

# parameter: opcodes with offsets
# makes all PUSH2 xyz JUMP and PUSH2 xyz JUMPI relative
# if only_within_codeblock is set True, it only replaces the value if xyz is within the start and end of this codeblock
def sanitize_opcodes_old(opc, only_within_codeblock=False):
    res = []
    min_address = int(opc[0][0], 16)
    max_address = int(opc[len(opc)-1][0], 16)
    for i in range(0, len(opc)-1):
        if opc[i][1].split(" ")[0] == "PUSH2":
            if opc[i+1][1] == "JUMP" or opc[i+1][1] == "JUMPI":
                target_address = int(opc[i][1].split(" ")[1], 16)
                if not only_within_codeblock or (target_address > min_address and target_address < max_address):
                    relative_jump_dest = target_address - int(opc[i][0], 16)
                    sign = ""
                    if relative_jump_dest > 0:
                        sign = "+"
                    res.append( (opc[i][0], "PUSH2 "+sign+hex(relative_jump_dest)) )
                    continue
        res.append(opc[i])
    res.append(opc[len(opc)-1])
    return res

# parameter: opcodes with offsets
# makes _all_ PUSH2 xyz instructions relative.
def sanitize_opcodes(opc):
    res = []
    for i in range(0, len(opc)):
        if opc[i][1].split(" ")[0] == "PUSH2":
            target_address = int(opc[i][1].split(" ")[1], 16)
            relative_jump_dest = target_address - int(opc[i][0], 16)
            sign = ""
            if relative_jump_dest > 0:
                sign = "+"
            res.append( (opc[i][0], "PUSH2 "+sign+hex(relative_jump_dest)) )
            continue
        res.append(opc[i])
    return res

def sanitize_bytecode(bytecode):
    return opcodes_to_bytecode(list(map(lambda x: x[1], sanitize_opcodes(bytecode_to_opcodes_with_offsets(bytecode)))))

def calculate_contract_address(tx_from, tx_nonce):
    return "0x" + eth.mk_contract_address(int(tx_from, 16), tx_nonce).hex()

def calculate_function_signature_hash(interface):
    return "0x" + eth.sha3(interface).hex()[:8]

def calculate_event_signature_hash(interface):
    return "0x" + eth.sha3(interface).hex()

# function gives the same result, no matter if `code` starts with "0x" or not
def calculate_code_hash(code):
    if code[:2] == "0x":
        code_to_hash = code[2:]
    else:
        code_to_hash = code
    return "0x" + eth.sha3(eth.decode_hex(code_to_hash)).hex()

# returns the minimum and maximum version of a list of versions
# example: get_min_max_versions(["1.3.4", "1.3.4.RC1", "1.3.5"]) == ('1.3.4.RC1', '1.3.5')
def get_min_max_versions(v_list):
    if len(v_list) == 0:
        return (None, None)
    sorted_list = sort_versions(v_list)
    return (sorted_list[0], sorted_list[-1])

def sort_versions(v_list):
    return sorted(v_list, key=functools.cmp_to_key(compare_versions))

# compare two version strings
# returns -1 if v1 < v2
#          0 if v1 = v2
#          1 if v1 > v2
def compare_versions(v1, v2):
    if v1 == v2:
        return 0
    if len(v1.split(".")) == 3:
        v1_splitted = v1+".99999"
    else:
        v1_splitted = v1.replace("RC", "")
    v1_splitted = list(map(int, v1_splitted.split(".")))
    if len(v2.split(".")) == 3:
        v2_splitted = v2+".99999"
    else:
        v2_splitted = v2.replace("RC", "")
    v2_splitted = list(map(int, v2_splitted.split(".")))
    for i in range(4):
        if v1_splitted[i] > v2_splitted[i]:
            return 1
        elif v1_splitted[i] < v2_splitted[i]:
            return -1

# returns the complete eth.compiler table
def get_all_compiler_versions(db):
    compiler_list = []
    c = db.cursor()
    query = f"""
        SELECT version, releaseDate
        FROM compiler
        ORDER BY releaseDate;
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        compiler_list.append( (result[0], result[1]) )
        result = c.fetchone()
    return compiler_list

# returns the complete eth.library table
def get_all_library_versions(db, lib):
    lib_list = []
    c = db.cursor()
    query = f"""
        SELECT version, releaseDate
        FROM library
        WHERE name = "{lib}"
        ORDER BY releaseDate;
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        lib_list.append( (result[0], result[1]) )
        result = c.fetchone()
    return lib_list
