#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import re
import base64
import collections
import statistics

import eth_util

def get_most_used_versions(db, complete_compiler_list, complete_safemath_list):
    batch_size = 10000
    offset = 0
    most_used_compiler_versions = collections.Counter()
    most_used_safemath_versions = collections.Counter()
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
                range_started = False
                for i in complete_compiler_list:
                    if i[0] == result[0]:
                        range_started = True
                    if range_started:
                        most_used_compiler_versions[i[0]] += 1
                    if i[0] == result[1]:
                        break
            if result[2] != None and result[3] != None:
                range_started = False
                for i in complete_safemath_list:
                    if i[0] == result[2]:
                        range_started = True
                    if range_started:
                        most_used_safemath_versions[i[0]] += 1
                    if i[0] == result[3]:
                        break
            result = c.fetchone()
        offset += batch_size

    print("Most used compiler versions of contract codes:")
    for r in sorted(most_used_compiler_versions.items()):
        print("{} - {}".format(r[0], r[1]))
    print()
    print("Most used SafeMath versions of contract codes:")
    for r in sorted(most_used_safemath_versions.items()):
        print("{} - {}".format(r[0], r[1]))

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

# script created for MA presentation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to get most used versions')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    complete_compiler_list = eth_util.get_all_compiler_versions(db)
    complete_safemath_list = eth_util.get_all_library_versions(db, "SafeMath")
    get_most_used_versions(db, complete_compiler_list, complete_safemath_list)
