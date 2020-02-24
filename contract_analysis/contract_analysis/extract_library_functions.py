#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import os
import re

import eth_util
import opcodes

class SearchInstructions():
    def __init__(self, library, function_name, starting_point, start_instructions, end_instructions):
        self.library = library
        self.function_name = function_name
        self.starting_point = starting_point
        self.start_instructions = start_instructions
        self.end_instructions = end_instructions

    def __str__(self):
        return self.library + " " + self.function_name

search_instructions = [
    SearchInstructions("SafeMath", "mul", "PUSH2 0x1111", ["search PUSH2", "JUMP there"], ["search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2"]),
    SearchInstructions("SafeMath", "div", "PUSH2 0x2222", ["search PUSH2", "JUMP there"], ["search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2"]),
    SearchInstructions("SafeMath", "add", "PUSH2 0x3333", ["search PUSH2", "JUMP there"], ["search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2"]),
    SearchInstructions("SafeMath", "sub", "PUSH2 0x4444", ["search PUSH2", "JUMP there"], ["search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2"]),
    SearchInstructions("SafeMath", "mod", "PUSH2 0x5555", ["search PUSH2", "JUMP there"], ["search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2"])
]

def extract_library_functions(user, password, dir_name, lib_name, lib_version):
    db = MySQLdb.connect(user=user, passwd=password, db="eth")
    c = db.cursor()
    print("{} version {}".format(lib_name, lib_version))
    for filename in sorted(os.listdir(dir_name)):
        with open(os.path.join(dir_name, filename), "r") as fd:
            bytecode = fd.readline()[:-1]
            if bytecode != "":
                contract_opcodes_with_offsets = eth_util.bytecode_to_opcodes_with_offsets(bytecode)
                contract_offsets, contract_opcodes = map(list, zip(*contract_opcodes_with_offsets))
                query = f"""
                    SELECT functions
                    FROM library
                    WHERE name = '{lib_name}'
                    AND version = '{lib_version}';
                """
                c.execute(query)
                supported_functions = c.fetchone()[0].split(",")
                for si in search_instructions:
                    if si.library == lib_name and si.function_name in supported_functions:
                        # print("{} - {}".format(filename, si.function_name))
                        if si.starting_point in contract_opcodes:
                            start_pos = contract_opcodes.index(si.starting_point)+1
                            end_pos = -1
                            last_push2 = "0x0"
                            for i in si.start_instructions:
                                if i == "search PUSH2":
                                    for j in range(start_pos, len(contract_opcodes)):
                                        if contract_opcodes[j].split(" ")[0] == "PUSH2":
                                            last_push2 = contract_opcodes[j].split(" ")[1]
                                            break
                                elif i == "JUMP there":
                                    if last_push2 in contract_offsets:
                                        start_pos = contract_offsets.index(last_push2)
                            for i in si.end_instructions:
                                if i == "search JUMPI INVALID STOP or REVERT STOP or JUMP without PUSH2":
                                    for j in range(start_pos+1, len(contract_opcodes_with_offsets)):
                                        if ((j >= 2 and contract_opcodes[j] == "STOP" and contract_opcodes[j-1] == "INVALID" and contract_opcodes[j-2] == "JUMPI")
                                            or (contract_opcodes[j] == "STOP" and contract_opcodes[j-1] == "REVERT")
                                            or (contract_opcodes[j] == "JUMP" and contract_opcodes[j-1].split(" ")[0] != "PUSH2")
                                            ):
                                            end_pos = j+1
                                            break
                            sanitized_opcodes_with_offsets = eth_util.sanitize_opcodes(contract_opcodes_with_offsets[start_pos:end_pos])
                            final_bytecode = eth_util.opcodes_to_bytecode([x[1] for x in sanitized_opcodes_with_offsets])
                            compiler_version = filename.split("-")[0]
                            compiler_optimization = bool(int(filename.split("-")[1]))
                            insert_into_db(db, compiler_version, compiler_optimization, lib_name, lib_version, si.function_name, final_bytecode)
                            # print(final_bytecode)

def insert_into_db(db, compiler_version, compiler_optimization, lib_name, lib_version, function_name, bytecode):
    c = db.cursor()
    c.execute("""INSERT INTO libraryFunction (compilerVersion, compilerOptimization, library, libraryVersion, functionName, bytecode)
        VALUES (%s, %s, %s, %s, %s, %s);""", (compiler_version, compiler_optimization, lib_name, lib_version, function_name, bytecode))
    db.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract library functions from multiple bytecode files')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--dirname', type=str, dest='dir_name', default='out/', help='Directory name')
    parser.add_argument('--libname', type=str, dest='lib_name', default='SafeMath', help='Name of the library')
    parser.add_argument('--libversion', type=str, dest='lib_version', default='1.0.0', help='Version of the library')
    args = parser.parse_args()

    extract_library_functions(args.user, args.password, args.dir_name, args.lib_name, args.lib_version)
