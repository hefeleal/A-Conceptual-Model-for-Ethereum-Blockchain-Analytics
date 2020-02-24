#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import re

import eth_util

class Function():
    def __init__(self, name, bytecode_list):
        self.name = name
        self.bytecode_list = bytecode_list

    def add_to_bytecode_list(self, bytecode):
        self.bytecode_list.append(bytecode)

    def __str__(self):
        return self.name + " [" + ", ".join(self.bytecode_list) + "]"

# returns a list of Function() objects. Each object contains the name of the function
# (e.g. add, sub, ...) and a list of all different bytecodes that were generated for
# this function
def get_library_functions(db, lib_name):
    c = db.cursor()
    query = f"""
        SELECT DISTINCT functionName, bytecode
        FROM libraryFunction
        WHERE library = '{lib_name}'
        ORDER BY functionName;
    """
    c.execute(query)
    library_functions = []
    result = c.fetchone()
    current_function = Function(result[0], [result[1]])
    result = c.fetchone()
    while result != None:
        if result[0] != current_function.name:
            library_functions.append(current_function)
            current_function = Function(result[0], [result[1]])
        else:
            current_function.add_to_bytecode_list(result[1])
        result = c.fetchone()
    library_functions.append(current_function)
    return library_functions

def find_library_occurrences(db, lib_name, lib_funs, complete_library_list):
    total_library_occurrences = 0
    c = db.cursor()
    query = f"""
        SELECT hash, code, occurrences, minCompilerVersion, maxCompilerVersion
        FROM contractCode;
        """
    c.execute(query)
    result = c.fetchone()
    while result != None:
        used_lib_funs = get_used_lib_functions(result[1], lib_funs)
        if len(used_lib_funs) > 0:
            total_library_occurrences += result[2]
            c2 = db.cursor()
            lib_column_name = "isUsing" + lib_name
            query = f"""
                UPDATE contractCode
                SET {lib_column_name}=true
                WHERE hash="{result[0]}";"""
            c2.execute(query)
            db.commit()
            possible_versions = get_possible_versions(db, used_lib_funs)
            # only take combinations of versions that are consistent with the minCompilerVersion
            # and maxCompilerVersion in the database; but overwrite the min/maxLibraryVersion in the db
            if result[3] != None:
                possible_versions = [x for x in possible_versions if eth_util.compare_versions(x[0], result[3]) >= 0 ]
            if result[4] != None:
                possible_versions = [x for x in possible_versions if eth_util.compare_versions(x[0], result[4]) <= 0 ]
            max_lib_version = get_max_lib_version(db, result[0], complete_library_list)
            if max_lib_version != None:
                possible_versions = [x for x in possible_versions if eth_util.compare_versions(x[1], max_lib_version) <= 0]
            # do not update the db if no consistent version-pair is found. We want to rather have
            # only the compiler version instead of nothing at all.
            if len(possible_versions) > 0:
                min_compiler, max_compiler = eth_util.get_min_max_versions([x[0] for x in possible_versions])
                min_lib, max_lib = eth_util.get_min_max_versions([x[1] for x in possible_versions])
                update_db(db, lib_name, result[0], min_compiler, max_compiler, min_lib, max_lib)
            # print("{} ({} occurrences)".format(result[0], result[2]))
            # for f in used_lib_funs:
            #     print("\t{} {}".format(f[0], f[1]))
            # print("Compiler Version {} - {}".format(min_compiler, max_compiler))
            # print("Library Version {} - {}".format(min_lib, max_lib))
            # print()
        result = c.fetchone()
    print(total_library_occurrences, "smart contracts use the library {}.".format(lib_name))

# if a contract was created before a library version was released,
# that library version definitely was not used
# but also consider one version higher than the latest one released
# because a nightly version could have been used as well!
def get_max_lib_version(db, hash, complete_library_list):
    c = db.cursor()
    query = f"""
            SELECT min(b.timestamp)
            FROM contract c, contractTransaction t, block b
            WHERE c.contractHash = "{hash}"
            AND c.transactionHash = t.hash
            AND t.blockNumber = b.blockNumber;
        """
    c.execute(query)
    result = c.fetchone()
    if result != None and result[0] != None:
        i = 0
        while i < len(complete_library_list)-1 and complete_library_list[i][1] <= result[0]:
            i += 1
        return complete_library_list[i][0]
    else: # it is a contract-created-contract
        query = f"""
            SELECT min(b.timestamp)
            FROM contractCreatedContract cc, contract c, contractTransaction t, block b
            WHERE cc.contractHash = "{hash}"
            AND cc.creatorAddress = c.address
            AND c.transactionHash = t.hash
            AND t.blockNumber = b.blockNumber;
        """
        c.execute(query)
        result = c.fetchone()
        if result != None and result[0] != None:
            i = 0
            while i < len(complete_library_list)-1 and complete_library_list[i][1] <= result[0]:
                i += 1
            return complete_library_list[i][0]
        else: # it is a contract-created-contract of generation >= 2
            return None

def update_db(db, lib_name, hash, min_compiler, max_compiler, min_lib, max_lib):
    if min_compiler == None:
        min_compiler_string = "NULL"
    else:
        min_compiler_string = "\"" + min_compiler + "\""
    if max_compiler == None:
        max_compiler_string = "NULL"
    else:
        max_compiler_string = "\"" + max_compiler + "\""
    if min_lib == None:
        min_lib_string = "NULL"
    else:
        min_lib_string = "\"" + min_lib + "\""
    if max_lib == None:
        max_lib_string = "NULL"
    else:
        max_lib_string = "\"" + max_lib + "\""
    lib_column_names = ("min"+lib_name+"Version", "max"+lib_name+"Version")
    c = db.cursor()
    query = f"""
        UPDATE contractCode
        SET minCompilerVersion={min_compiler_string}, maxCompilerVersion={max_compiler_string}, {lib_column_names[0]}={min_lib_string}, {lib_column_names[1]}={max_lib_string}
        WHERE hash="{hash}";"""
    c.execute(query)
    db.commit()

# returns a list of tuples containing function names and corresponding bytecodes that this
# smart contract bytecode contains.
def get_used_lib_functions(bytecode, lib_funs):
    ret = []
    for l in lib_funs:
        for b in l.bytecode_list:
            regex = re.findall(b.replace("x", "."), bytecode, re.S)
            if len(regex) > 0:
                ret.append( (l.name, b) )
                break
    return ret

# returns a list of (compilerVersion, libraryVersion) tuples that are possible for
# this combination of functions that are used together in a smart contract
def get_possible_versions(db, used_lib_funs):
    if len(used_lib_funs) == 0:
        return []
    c = db.cursor()
    query = "SELECT f0.compilerVersion, f0.libraryVersion FROM\n"
    function_id = 0
    for l in used_lib_funs:
        query += "(SELECT compilerVersion, libraryVersion FROM eth.libraryFunction WHERE bytecode = '" + l[1] + "') f" + str(function_id) + ",\n"
        function_id += 1
    query = query[:-2] + "\n" # remove comma from last subquery

    if len(used_lib_funs) > 1:
        query += "WHERE f0.compilerVersion = f1.compilerVersion AND f0.libraryVersion = f1.libraryVersion\n"
        for i in range(2, function_id):
            query += "AND f0.compilerVersion = f"+str(i)+".compilerVersion AND f0.libraryVersion = f"+str(i)+".libraryVersion\n"
    query += ";"
    c.execute(query)
    ret = []
    result = c.fetchone()
    while result != None:
        ret.append( (result[0], result[1]) )
        result = c.fetchone()
    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find contracts that implement a certain library and output the possible library and compiler versions')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--libname', type=str, dest='lib_name', default='SafeMath', help='Name of the library')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    lib_funs = get_library_functions(db, args.lib_name)
    complete_library_list = eth_util.get_all_library_versions(db, args.lib_name)
    find_library_occurrences(db, args.lib_name, lib_funs, complete_library_list)
