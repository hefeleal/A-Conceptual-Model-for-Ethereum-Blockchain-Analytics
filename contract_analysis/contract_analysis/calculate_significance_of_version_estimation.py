#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import re
import base64
import collections
import statistics

import eth_util

def get_distance_of_min_max_versions(db, complete_compiler_list, complete_safemath_list):
    batch_size = 10000
    offset = 0
    compiler_distances_of_contract_codes = []
    compiler_distances_of_contracts = []
    lib_distances_of_contract_codes = []
    lib_distances_of_contracts = []
    while True:
        c = db.cursor()
        query = f"""
            SELECT minCompilerVersion, maxCompilerVersion, minSafeMathVersion, maxSafeMathVersion, occurrences
            FROM contractCode
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            if result[0] != None and result[1] != None:
                c_distance = get_distance(complete_compiler_list, result[0], result[1])
                compiler_distances_of_contract_codes.append(c_distance)
                compiler_distances_of_contracts.extend([c_distance] * result[4])
            if result[2] != None and result[3] != None:
                lib_distance = get_distance(complete_safemath_list, result[2], result[3])
                lib_distances_of_contract_codes.append(lib_distance)
                lib_distances_of_contracts.extend([lib_distance] * result[4])
            result = c.fetchone()
        offset += batch_size
    print("Average compiler distance of contract codes: {:.4} (median: {:.4})".format(float(statistics.mean(compiler_distances_of_contract_codes)), float(statistics.median(compiler_distances_of_contract_codes))))
    print("Average compiler distance of contracts: {:.4} (median: {:.4})".format(float(statistics.mean(compiler_distances_of_contracts)), float(statistics.median(compiler_distances_of_contracts))))
    print("Average lib distance of contract codes: {:.4} (median: {:.4})".format(float(statistics.mean(lib_distances_of_contract_codes)), float(statistics.median(lib_distances_of_contract_codes))))
    print("Average lib distance of contracts: {:.4} (median: {:.4})".format(float(statistics.mean(lib_distances_of_contracts)), float(statistics.median(lib_distances_of_contracts))))

    compiler_distances_of_contract_codes_counter = collections.Counter(compiler_distances_of_contract_codes)
    print("Compiler distances of contract codes:")
    for r in sorted(compiler_distances_of_contract_codes_counter.items()):
        print("{} - {}".format(r[0], r[1]))
    print()
    compiler_distances_of_contracts_counter = collections.Counter(compiler_distances_of_contracts)
    print("Compiler distances of contracts:")
    for r in sorted(compiler_distances_of_contracts_counter.items()):
        print("{} - {}".format(r[0], r[1]))
    print()
    lib_distances_of_contract_codes_counter = collections.Counter(lib_distances_of_contract_codes)
    print("Lib distances of contract codes:")
    for r in sorted(lib_distances_of_contract_codes_counter.items()):
        print("{} - {}".format(r[0], r[1]))
    print()
    lib_distances_of_contracts_counter = collections.Counter(lib_distances_of_contracts)
    print("Lib distances of contracts:")
    for r in sorted(lib_distances_of_contracts_counter.items()):
        print("{} - {}".format(r[0], r[1]))
    print()

def get_distance(complete_list, low, high):
    low_id = 0
    high_id = 0
    i = 0
    for c in complete_list:
        if c[0] == low:
            low_id = i
        if c[0] == high:
            high_id = i
            break
        i += 1
    return high_id - low_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to see if the results are even significant')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    complete_compiler_list = eth_util.get_all_compiler_versions(db)
    complete_safemath_list = eth_util.get_all_library_versions(db, "SafeMath")
    get_distance_of_min_max_versions(db, complete_compiler_list, complete_safemath_list)
