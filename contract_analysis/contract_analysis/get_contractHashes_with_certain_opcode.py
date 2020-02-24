#!/usr/bin/python3
# coding=utf-8

import MySQLdb
import argparse

import eth_util

def run_query(user, password, opcode):
    db = MySQLdb.connect(user=user, passwd=password, db="eth")
    batch_size = 10000
    offset = 0
    while True:
        c = db.cursor()
        query = f"""
            SELECT code, hash, occurrences
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
                if o == opcode:
                    print("{} ({} occurrences)".format(result[1], result[2]), flush=True)
                    break
            result = c.fetchone()
        offset += batch_size

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print all contract hashes whose code contains a certain opcode')
    parser.add_argument('--mysql-user', type=str, dest='user', default='user', help='MySQL Username')
    parser.add_argument('--mysql-password', type=str, dest='password', default='password', help='MySQL Password')
    parser.add_argument('--opcode', type=str, dest='opcode', default=None, help='Opcode to search')
    args = parser.parse_args()
    run_query(args.user, args.password, args.opcode)
