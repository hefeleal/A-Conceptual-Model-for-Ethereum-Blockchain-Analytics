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
    addresses = collections.Counter()
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
                if o[:6] == "PUSH20":
                    if (len(o[7:]) == 42 and o[7:] != "0xffffffffffffffffffffffffffffffffffffffff"
                        and o[7:] != "0x0000000000000000000000000000000000000000"):
                        addresses[o[7:]] += result[1]
            result = c.fetchone()
        offset += batch_size
    i = 1
    for f in addresses.most_common():
        print("{:02}. {} - {}".format(i, f[1], f[0]))
        i += 1
        if i == 100:
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract hard-coded addresses from bytecode')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    db = MySQLdb.connect(user=args.user, passwd=args.password, db="eth")
    run_query(db)
