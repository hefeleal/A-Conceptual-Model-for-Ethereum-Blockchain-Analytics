#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse
import collections
import json

import eth_util

def run_query(user, password):
    db = MySQLdb.connect(user=user, passwd=password, db="eth")
    batch_size = 10000
    offset = 0
    function_hashes = collections.Counter()
    while True:
        c = db.cursor()
        query = f"""
            SELECT address, contractCreationCode
            FROM contract
            WHERE contractHash != "0xc5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
            LIMIT {batch_size}
            OFFSET {offset};
            """
        c.execute(query)
        result = c.fetchone()
        if result == None: # offset exceeded dataset
            break
        while result != None:
            opcodes = eth_util.bytecode_to_opcodes(result[1])
            if "SELFDESTRUCT" in opcodes:
                print("{} {}".format(result[0], result[1]), flush=True)
            result = c.fetchone()
        offset += batch_size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find constructors with SELFDESTRUCT opcode')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    args = parser.parse_args()
    run_query(args.user, args.password)
