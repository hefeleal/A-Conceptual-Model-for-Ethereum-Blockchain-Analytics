#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import collections
import json

import eth_util

def run_query(db):
    batch_size = 10000
    offset = 0
    function_hashes = collections.Counter()
    while True:
        c = db.cursor()
        query = f"""
            SELECT code, occurrences
            FROM contractCode
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            opcodes = eth_util.bytecode_to_opcodes(result[0])
            for o in opcodes:
                if o[:5] == "PUSH4":
                    if o[6:] != "0xffffffff" and o[6:] != "0x01000000":
                        function_hashes[o[6:]] += result[1]
            result = c.fetchone()
        offset += batch_size
    not_found_sigs = 0
    i = 1
    for f in function_hashes.most_common():
        sig = lookup_sig(db, f[0])
        if sig == f[0]:
            not_found_sigs += 1
        print("{:02}. {} - {}".format(i, f[1], sig))
        i += 1
    print("{} function signatures not found".format(not_found_sigs))

def lookup_sig(db, hash):
    c = db.cursor()
    query = f"""
        SELECT interface
        FROM functions
        WHERE hash='{hash}';
        """
    c.execute(query)
    result = c.fetchone()
    if result == None:
        return hash
    else:
        return result[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract function hashes')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    run_query(db)
